# Template And Patterns

Используй этот файл, когда нужно быстро написать новый `SKILL.md`, переписать
монолитный навык или выбрать паттерн для дорогого failure mode.

## Minimal `SKILL.md` Template

```markdown
---
name: my-advanced-skill
description: >-
  <Глаголы и домен>. Используй, когда нужно <trigger 1>, <trigger 2>,
  <trigger 3>, включая <formats/tools/contexts>.
---

# My Advanced Skill

Ты — <роль агента>.

## Principle 0

<Самая дорогая ошибка домена и операционное правило, которое ее предотвращает.>

## Workflow

1. Уточни задачу и обязательные входные данные.
2. Осмотри локальный контекст или пользовательские артефакты.
3. Выбери минимальный надежный путь.
4. Прочитай только релевантные bundled resources.
5. Выполни работу.
6. Проверь результат.
7. Сообщи ограничения, артефакты и следующие шаги.

## Resource Routing

| Задача | Читать/запускать | Зачем |
|---|---|---|
| Нужен полный процесс | `references/workflow.md` | Полный процесс |
| Нужна доменная схема | `references/schema.md` | Schema/source of truth |
| Нужно проверить результат | `scripts/verify.*` | Детерминированная проверка |

## Constraints

- Не выдумывай отсутствующие факты.
- Не обещай неподдерживаемые форматы.
- Не читай references и не создавай ресурсы без маршрута из `SKILL.md`.
- Не заменяй обязательный script/manual pipeline без явного blocker.

## Validation

- Проверь frontmatter, ссылки, пути и layer coherence.
- Проверь, что обязательные шаги нельзя обойти через optional wording.
- Запусти smoke tests для scripts.
- Для сложных изменений проведи forward-testing.
```

## Failure-Mode Guardrails

Для каждого дорогого сбоя добавь симптом, причину, действие агента и
проверку, что сбой устранен.

Пример:

```markdown
- Если API schema не найдена, не пиши запрос по памяти. Сначала найди
  актуальную schema или спроси пользователя.
```

## Decision Tree

Используй, когда есть несколько технических путей:

```markdown
Если нужен редактируемый результат, используй путь A.
Если нужен pixel-perfect preview, используй путь B.
Если исходных данных не хватает, остановись и спроси пользователя.
```

## Mandatory Step Guardrail

Используй для критичных шагов, которые агент не должен обходить.

```markdown
Если <condition>, обязательно выполни <action> через <resource/script>.
Проверь результат через <validation>.
Если <resource/script> недоступен, остановись, назови blocker и риск.
Не заменяй этот шаг best-effort или ручным эквивалентом без явного waiver.
```

Хороший guardrail делает обход дороже, чем честную остановку: агент понимает,
когда шаг обязателен, чем его проверить и как корректно сдать blocker.

## Deterministic Scripts

Выноси в script все, что агент будет иначе каждый раз переписывать:

- парсинг;
- конвертацию форматов;
- валидацию;
- экспорт;
- bulk transforms;
- работу с хрупкими XML/JSON/binary форматами.

Script должен иметь usage, понятные ошибки и smoke test.

## Reference Shards

Разделяй большие знания по задачам, а не по абстрактным темам.

Лучше: `references/import-csv.md`, `references/export-pdf.md`,
`references/schema-validation.md`.

Хуже: `references/all-docs.md`, `references/misc.md`,
`references/everything.md`.

## Forward-Testing

Формат запроса проверяющему агенту:

```text
Use the skill at <path> to solve this user request: <realistic request>.
Return what you did, artifacts produced, validation run, and blockers.
```

Не пиши:

```text
Review this skill and check whether it fixed problem X that I noticed.
```

Такой запрос протекает ответом и не проверяет переносимость.
