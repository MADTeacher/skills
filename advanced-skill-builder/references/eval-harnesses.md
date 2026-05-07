# Eval Harnesses

Используй этот файл, когда eval-кейсы нужно запускать в разных агентских CLI.
Основной контракт общий, а команды ниже являются runner adapters. Не привязывай
core workflow навыка к одному harness.

Справочные страницы для проверки adapter-команд:

- https://docs.cursor.com/en/cli/reference/output-format
- https://opencode.ai/docs/cli/
- https://pi.dev/docs/latest/json
- https://pi.dev/docs/latest/rpc
- https://code.claude.com/docs/en/cli-reference

## Общий контракт

Перед запуском подготовь переменные:

```bash
SKILL_DIR="/abs/path/to/.agents/skills/<skill-name>"
RUN_DIR="/abs/path/to/evals/runs/<eval-id>/<timestamp>"
PROMPT="Use the skill at $SKILL_DIR to solve this user request: ..."
SCHEMA="/abs/path/to/schema.json"
SESSION_ID="..."
mkdir -p "$RUN_DIR"
```

Harness adapter должен дать хотя бы один машинно или вручную проверяемый
артефакт: `events.ndjson`, `result.json`, `result.txt` или `session.json`.
Если adapter не умеет tool events, сохраняй transcript и честно помечай
недоступные метрики.

## Adapter Matrix

| Adapter | Команда | События | Итог | Ограничения |
|---|---|---|---|---|
| `codex` | `codex exec --json "$PROMPT" > "$RUN_DIR/events.ndjson"` | JSONL events в stdout | `result.txt` через `-o`, если нужен финальный ответ | Проверить локальную версию `codex exec --help`; `-o` пишет last message |
| `cursor` | `cursor-agent --print --output-format stream-json "$PROMPT" > "$RUN_DIR/events.ndjson"` | NDJSON | terminal result event | `--output-format` работает только с `--print`; skill path может идти через prompt или project config |
| `opencode` | `opencode run --format json "$PROMPT" > "$RUN_DIR/events.ndjson"` | raw JSON events | session id в events | Skill loading зависит от config, agent и cwd |
| `pi` | `pi --mode json --skill "$SKILL_DIR" --no-session "$PROMPT" > "$RUN_DIR/events.ndjson"` | JSONL session events | event stream | `--skill` явный; можно добавить `--no-context-files` для более чистого запуска |
| `claude-code` | `claude -p "$PROMPT" --output-format stream-json > "$RUN_DIR/events.ndjson"` | NDJSON | final result event | Навык должен быть доступен среде Claude Code или передан через prompt/settings |
| `generic` | Команда проекта из `adapter_notes` | По возможности NDJSON | Любой проверяемый файл | Нужно описать, где лежат transcript, timing и grading |

## Codex

Базовый запуск:

```bash
codex exec --json "$PROMPT" > "$RUN_DIR/events.ndjson"
```

JSONL события пишутся в stdout. Если нужен отдельный финальный ответ:

```bash
codex exec --json "$PROMPT" -o "$RUN_DIR/result.txt" > "$RUN_DIR/events.ndjson"
```

Рубрика со строгим JSON, если текущий CLI поддерживает schema output:

```bash
codex exec --json "$PROMPT" --output-schema "$SCHEMA" \
  -o "$RUN_DIR/grading.json" > "$RUN_DIR/events.ndjson"
```

Перед фиксацией adapter в skill проверь `codex exec --help`, потому что флаги
вывода зависят от установленной версии.

## Cursor CLI

Streaming events:

```bash
cursor-agent --print --output-format stream-json "$PROMPT" > "$RUN_DIR/events.ndjson"
```

Итоговый JSON:

```bash
cursor-agent --print --output-format json "$PROMPT" > "$RUN_DIR/result.json"
```

В `stream-json` сохраняются события выполнения. В `json` итог собирается в
одно поле `result`, поэтому для проверки tool sequence лучше брать stream.

## OpenCode

Raw JSON events:

```bash
opencode run --format json "$PROMPT" > "$RUN_DIR/events.ndjson"
```

Экспорт полной сессии:

```bash
opencode export "$SESSION_ID" > "$RUN_DIR/session.json"
```

Если используется `opencode serve`, adapter может подключаться к уже поднятому
серверу:

```bash
opencode run --attach http://localhost:4096 --format json "$PROMPT" > "$RUN_DIR/events.ndjson"
```

## Pi

JSON event stream:

```bash
pi --mode json --skill "$SKILL_DIR" --no-session "$PROMPT" > "$RUN_DIR/events.ndjson"
```

Print mode:

```bash
pi -p --skill "$SKILL_DIR" --no-session "$PROMPT" > "$RUN_DIR/result.txt"
```

RPC mode для интеграций:

```bash
pi --mode rpc --no-session
```

После старта RPC отправляй JSONL-команды по stdin и сохраняй stdout как
`events.ndjson` или отдельный protocol log. Конкретный payload бери из текущей
документации RPC, если adapter пишется в коде.

## Claude Code

Streaming events:

```bash
claude -p "$PROMPT" --output-format stream-json > "$RUN_DIR/events.ndjson"
```

Итоговый JSON:

```bash
claude -p "$PROMPT" --output-format json > "$RUN_DIR/result.json"
```

Строгий JSON для rubric grader:

```bash
claude -p "$PROMPT" --output-format json --json-schema "$(cat "$SCHEMA")" > "$RUN_DIR/grading.json"
```

Если нужно больше диагностики, добавь `--verbose` и сохрани stderr отдельно:

```bash
claude -p "$PROMPT" --output-format stream-json --verbose \
  > "$RUN_DIR/events.ndjson" 2> "$RUN_DIR/stderr.log"
```

## Нормализация результата

После каждого запуска приведи данные к общей форме:

```json
{
  "adapter": "cursor",
  "eval_id": "create-basic-skill",
  "status": "pass",
  "artifacts": {
    "events": "events.ndjson",
    "result": "result.json",
    "grading": "grading.json"
  },
  "metrics": {
    "wall_time_ms": 1234,
    "turns": 4,
    "tokens": null,
    "unavailable_reason": "adapter did not report token usage"
  }
}
```

Не смешивай adapter-specific поля с eval assertions. Сначала сохрани сырой
output, потом делай нормализацию и grading.
