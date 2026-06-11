# Skills

Репозиторий с персональными агентскими навыками: от TDD и диагностики багов до генерации PRD, декомпозиции задач, дизайна,
диаграмм и презентаций.

## Как установить

Навыки можно подключать по одному или сразу весь каталог. В любом варианте итоговая
структура должна привести к тому, что нужный `SKILL.md` лежит внутри
`.agents/skills/<skill-name>/`, находящейся в корневой диретории проекта (либо на глобальном уровне)
или директории skills вашего конкретного harness (.cursor, .codex и т.д.)

### Вручную

Скопируйте нужные папки навыков в директорию агента:

```bash
mkdir -p .agents/skills
cp -R path/to/skills/tdd .agents/skills/
```

Для установки нескольких навыков скопируйте несколько папок:

```bash
cp -R path/to/skills/{tdd,design-studio,prd-from-context} .agents/skills/
```

После копирования структура должна выглядеть так:

```text
.agents/skills/
  tdd/
    SKILL.md
  design-studio/
    SKILL.md
```

### Через git clone

Если удобнее держать каталог навыков рядом с проектом, клонируйте репозиторий и
скопируйте нужные папки:

```bash
git clone https://github.com/MADTeacher/skills.git
mkdir -p .agents/skills
cp -R skills/tdd .agents/skills/
```

### Через npx

Для установки через CLI используйте `skills add`. Можно поставить все навыки:

```bash
npx skills add MADTeacher/skills --skill '*' --agent universal
```

Или только конкретный навык:

```bash
npx skills add MADTeacher/skills --skill tdd --agent universal
```

## Доступные навыки

| Навык | Краткое назначение | SKILL |
| --- | --- | --- |
| `advanced-skill-builder` | Создание, переработка, аудит и проверка продвинутых агентских навыков, включая структуру skill-проекта, resource routing, validation, evals и smoke tests. | [SKILL.md](./advanced-skill-builder/SKILL.md) |
| `artistic-svg-director` | Создание, доработка, проверка, PNG-рендер и художественная оценка сложных SVG-иллюстраций и векторных ассетов. | [SKILL.md](./artistic-svg-director/SKILL.md) |
| `briefmode` | Режим сверхсжатой коммуникации для экономии токенов без потери технической точности. | [SKILL.md](./briefmode/SKILL.md) |
| `bug-fix-task` | Диагностика багов, поиск корневой причины и формирование задачи на исправление с TDD-планом. | [SKILL.md](./bug-fix-task/SKILL.md) |
| `design-studio` | Создание и ревью дизайн-артефактов: интерфейсов, лендингов, прототипов, визуальных направлений и дизайн-аудитов. | [SKILL.md](./design-studio/SKILL.md) |
| `drawio-diagrams` | Создание, редактирование, проверка и экспорт диаграмм `draw.io` / `diagrams.net` в редактируемом виде и графических форматах. | [SKILL.md](./drawio-diagrams/SKILL.md) |
| `mermaid-diagrams` | Создание, проверка, PNG-рендер и визуальное ревью Mermaid-диаграмм с обязательной оценкой языковой моделью. | [SKILL.md](./mermaid-diagrams/SKILL.md) |
| `presentation-design` | Создание, доработка, последовательная проверка и экспорт презентаций в HTML, PPTX, PDF, PNG и связанных форматах. | [SKILL.md](./presentation-design/SKILL.md) |
| `prd-from-context` | Сборка PRD на русском языке из уже имеющегося контекста, требований и понимания кодовой базы без дополнительного интервью. | [SKILL.md](./prd-from-context/SKILL.md) |
| `prd-to-vertical-slice-tasks` | Декомпозиция PRD, плана или спецификации в независимые задачи через вертикальные срезы. | [SKILL.md](./prd-to-vertical-slice-tasks/SKILL.md) |
| `solution-interview` | Последовательное интервью по проекту, фиче, багу или архитектурному решению для полного прояснения задачи и вариантов решения. | [SKILL.md](./solution-interview/SKILL.md) |
| `tdd` | Реализация фич и исправлений по циклу red-green-refactor с опорой на один поведенческий тест за шаг. | [SKILL.md](./tdd/SKILL.md) |
