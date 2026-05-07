# Eval Design

Используй этот файл, когда пользователь явно просит eval-контур, benchmark,
регрессию поведения, test prompts или проверку работоспособности агентского
навыка. Верхний слой навыка говорит, когда eval включается. Тут описан сам
протокол.

Основные источники идей:

- https://developers.openai.com/blog/eval-skills
- https://agentskills.io/skill-creation/evaluating-skills

## Eval Layer Gate

Перед созданием eval suite зафиксируй измеримый успех:

- какой пользовательский запрос должен сработать;
- какие файлы, ответы или артефакты должны появиться;
- какие ошибки нельзя принять как PASS;
- какой harness запускает агента и где сохраняет evidence.

Если успех нельзя проверить, сначала перепиши навык или запрос. Размытый eval
быстро превращается в ручную оценку вкуса.

## Структура eval suite

Канонический файл:

```text
evals/evals.json
```

Минимальная форма:

```json
{
  "version": 1,
  "evals": [
    {
      "id": "create-basic-skill",
      "title": "Создание навыка с проверкой",
      "harness_adapter": "generic",
      "prompt": "Use the skill at <path> to solve this user request: ...",
      "expected_output": "Создан SKILL.md, есть routing, validation и итоговый отчет.",
      "files": [],
      "assertions": [
        {
          "type": "artifact_exists",
          "path": ".agents/skills/example-skill/SKILL.md"
        },
        {
          "type": "contains",
          "target": "final_response",
          "value": "проверено"
        }
      ],
      "grading": {
        "method": "rubric",
        "pass_score": 0.8
      }
    }
  ]
}
```

`harness_adapter` выбирай из списка: `codex`, `cursor`, `opencode`, `pi`,
`claude-code`, `generic`. Если нужен другой runner, используй `generic` и
запиши команду в `adapter_notes`.

## Outputs

Каждый запуск eval-кейса должен писать артефакты в отдельную папку:

```text
evals/runs/<eval-id>/<timestamp>/
```

Ожидаемые файлы:

| Файл | Когда нужен | Что хранит |
|---|---|---|
| `events.ndjson` | Harness умеет streaming JSON | JSONL события, tool calls, промежуточные сообщения |
| `result.json` | Harness умеет итоговый JSON | Финальный ответ, session id, метрики, если они есть |
| `result.txt` | JSON недоступен | Человеческий transcript или финальный ответ |
| `timing.json` | Делается benchmark | wall time, turn count, tokens, cost, если harness это отдает |
| `grading.json` | Есть script или rubric grader | PASS/FAIL, score, evidence и причины |
| `benchmark.json` | Сравниваются варианты | baseline, variant, pass rate, regressions |

Если harness не отдает tool events или tokens, не выдумывай метрики. Запиши
`null` и поле `unavailable_reason`.

## Assertions

Детерминированные assertions предпочтительнее рубрик, когда результат можно
проверить файлом, схемой, командой или строкой.

Поддерживаемые типы для `scripts/validate-eval-suite.py`:

- `artifact_exists`;
- `contains`;
- `not_contains`;
- `regex`;
- `json_field`;
- `schema_valid`;
- `script_exit_zero`;
- `rubric_score`;
- `manual_review`;
- `harness_event`;
- `metric_available`.

Каждая assertion должна иметь `type` и проверяемую цель: `path`, `target`,
`value`, `pattern`, `command`, `schema` или `metric`.

## Grading

Используй `method: "script"`, если проверку можно выполнить локально. Это
лучший вариант для форматов, схем, артефактов, команд и регрессии.

Используй `method: "rubric"`, если качество зависит от смысла. Рубрика должна
требовать evidence: какие строки ответа, файлы или события доказывают PASS.

Используй `method: "manual"` только для первого набора или спорного доменного
качества. Такой eval нельзя считать автоматической регрессией.

## Benchmark

Benchmark нужен только когда пользователь явно просит benchmark или сравнение
вариантов внутри eval-контура. Сравнивай:

- новая версия навыка против старой;
- новая версия против запуска без навыка;
- разные harness adapters на одном prompt;
- разные модели или permissions, если это влияет на результат.

Сохраняй в `benchmark.json` минимум: `baseline`, `variant`, `eval_ids`,
`pass_rate`, `regressions`, `notes`.

## Блокеры

Остановись и назови риск, если:

- eval требует секреты, платный доступ или network, которых нет;
- harness не установлен и нет generic runner;
- expected output нельзя проверить без скрытого ответа автора;
- prompt подсказывает правильное решение вместо проверки переносимости.
