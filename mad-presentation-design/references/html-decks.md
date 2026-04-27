# HTML-деки, экспорт и проверка

HTML — рабочий исходник этого навыка. Статические экспорты строятся из HTML,
кроме редактируемого PPTX: для него нужен constrained HTML с самого начала.

## Первое решение: формат сдачи

Спросите или выведите из задачи:

- только HTML: максимальная свобода;
- редактируемый PPTX: constrained source, см. `pptx-authoring.md`;
- PDF: печать/экспорт из браузера, высокая визуальная точность;
- PNG: скриншоты по слайдам;
- SVG: constrained/best-effort путь; надежен только для простых нативных
  векторных слайдов или специально подготовленных SVG-ассетов.

## Размеры canvas

По умолчанию:

- HTML/PDF/PNG: `1920x1080px`;
- редактируемый PPTX: `960x540pt`, соответствует PowerPoint wide.

Другие размеры используйте только по требованию площадки, шаблона или задачи.

## 2-слайдовое направление до массовой сборки

Перед созданием всего дека сделайте:

1. обложку;
2. репрезентативный плотный контентный слайд.

Эти два слайда фиксируют грамматику: типографику, интервалы, палитру,
изображения, графики, footer и экспортные ограничения.

## Multi-file архитектура

Используйте по умолчанию для серьезных деков.

```text
deck/
├── index.html
├── shared/
│   ├── tokens.css
│   └── components.css
└── slides/
    ├── 01-cover.html
    ├── 02-agenda.html
    └── 03-content.html
```

Стартуйте с `assets/deck_index.html` и отредактируйте `DECK_MANIFEST`.

Плюсы:

- ошибка одного слайда не ломает весь дек;
- каждый слайд можно открыть отдельно;
- CSS и layout-проблемы проще изолировать;
- разные люди могут работать над разными слайдами.

## Single-file архитектура

Для маленьких деков и быстрых черновиков используйте `assets/deck_stage.js`.

```html
<script src="assets/deck_stage.js"></script>
<deck-stage>
  <section class="slide">...</section>
  <section class="slide">...</section>
</deck-stage>
```

Каждый `section` должен иметь фиксированные размеры и `overflow: hidden`.

## Грамматика слайда

Базовый слайд:

```html
<section class="slide">
  <p class="kicker">Раздел</p>
  <h1>Заголовок слайда</h1>
  <p class="lead">Главная мысль.</p>
  <div class="content-grid">...</div>
  <p class="slide-number">03</p>
</section>
```

Правила:

- одна главная мысль на слайд;
- body text обычно `24px` или больше на `1920x1080`;
- captions обычно `18px` или больше;
- поля и номера слайдов стабильны;
- роли слайдов чередуются.

## React/Babel

Используйте React только когда он уменьшает повторение: компоненты графиков,
повторяемые slide layouts, variant canvas или общие data-driven секции. Для
маленьких деков часто достаточно plain HTML/CSS.

Подключение:

```html
<script src="https://unpkg.com/react@18.3.1/umd/react.development.js" crossorigin="anonymous"></script>
<script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js" crossorigin="anonymous"></script>
<script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js" crossorigin="anonymous"></script>
```

Компоненты подключайте как Babel scripts:

```html
<script type="text/babel" src="components.jsx"></script>
<script type="text/babel" src="deck.jsx"></script>
```

Каждый Babel-файл компилируется отдельно. Общие компоненты экспортируйте в
`window`.

```jsx
function MetricCard({ label, value }) {
  return (
    <div className="metric-card">
      <p>{label}</p>
      <strong>{value}</strong>
    </div>
  );
}

window.MetricCard = MetricCard;
```

Держите данные слайдов в JSON-compatible объектах:

```js
window.DECK_DATA = {
  metrics: [
    { label: 'Revenue', value: '$12.4M' },
  ],
};
```

Используйте уникальные имена компонентов и стилей для каждого дека. Избегайте
глобальных `styles`, `data` или `Card`, если загружается несколько scripts.

Редактируемый PPTX читает rendered DOM. Если нужен PPTX, финальный текст должен
быть в семантических текстовых тегах, а browser-only эффекты лучше исключить.

## Заметки докладчика

Используйте `aside.notes` или JSON-блок заметок. Notes помогают выступать, а не
дублируют видимый текст.

```html
<aside class="notes">
  Перед следующим слайдом объяснить, почему изменилась метрика.
</aside>
```

## PDF-экспорт

Multi-file:

```bash
node scripts/export_deck_pdf.mjs --slides deck/slides --out deck.pdf
```

Single-file `deck-stage`:

```bash
node scripts/export_deck_stage_pdf.mjs --html deck.html --out deck.pdf
```

PDF должен сохранять визуальную точность и searchable text, если браузер может
напечатать текст как вектор.

## PNG-экспорт

PNG подходит для ревью, thumbnail и статичной отправки слайдов.

```bash
node scripts/export_deck_png.mjs --slides deck/slides --out deck/png
```

Проверьте загрузку шрифтов до скриншотов. Скрипт ждет browser idle и
`document.fonts.ready`.

## SVG-экспорт

SVG не является универсальным экспортом произвольного HTML. Используйте один из
путей:

- сделайте слайд или ключевой visual как нативный SVG, если нужен настоящий
  вектор;
- экспортируйте графики/диаграммы как SVG-ассеты и вставляйте их в HTML-дек;
- для произвольных HTML-слайдов сдавайте PDF/PNG и честно объясняйте, почему
  SVG будет lossy или неремонтируемым.

## Редактируемый PPTX

Команда:

```bash
node scripts/export_deck_pptx.mjs --slides deck/slides --out deck.pptx
```

Сначала прочитайте `pptx-authoring.md`. Если исходный дек был сделан без PPTX
constraints, сначала перестройте HTML в constrained version.

## Проверка результата

Каждый HTML-дек нужно проверить визуально и технически до сдачи.

Чеклист:

1. HTML открывается в браузере.
2. В консоли нет релевантных ошибок.
3. Шрифты и изображения загружаются.
4. Ключевые слайды читаются в целевом размере.
5. Скриншоты слайдов совпадают с макетом.
6. Запрошенные экспорты созданы и просмотрены.
7. Если был запрошен PPTX, файл открыт и текст проверен на редактируемость.

Базовая проверка браузера:

```bash
python scripts/verify.py deck/index.html
```

Для `deck-stage` файла:

```bash
python scripts/verify.py deck.html --slides 12
```

Проверка viewport:

```bash
python scripts/verify.py deck/index.html --viewports 1920x1080,1440x900
```

Скриншоты слайдов:

```bash
python scripts/verify.py deck.html --slides 10 --output deck/screenshots
```

Ищите:

- обрезанный текст;
- плохое выравнивание;
- нечитаемые подписи графиков;
- пропавшие изображения;
- съехавшие footer или номера;
- несовместимые отступы между слайдами.

## Проверка экспортов

PDF:

- число страниц совпадает с числом слайдов;
- фоны видны;
- текст searchable, когда это ожидается;
- нет пустой страницы в конце.

PNG:

- число файлов совпадает с числом слайдов;
- изображения достаточно четкие для ревью;
- прозрачные ассеты отображаются корректно.

SVG:

- обещайте SVG-качество только для constrained vector-authored slides;
- откройте SVG хотя бы в одном viewer;
- назовите rasterized или non-editable части, если они есть.

PPTX:

- текст редактируется;
- изображения не пропали;
- границы слайда соблюдены;
- визуальные упрощения намеренные.

## Частые сбои

Пустой или частичный рендер:

- неверный локальный путь;
- не хватает зависимости;
- JSX syntax issue;
- компонент не прикреплен к `window` при отдельных Babel-файлах.

Неверный шрифт:

- проверьте пути `@font-face`;
- ждите `document.fonts.ready`;
- не полагайтесь на шрифт, которого нет в export environment.

Съехал layout:

- проверьте `box-sizing: border-box`;
- проверьте ширину и высоту слайда;
- посмотрите grid tracks и absolute-positioned элементы;
- проверьте, использует ли экспорт `px` или `pt`.

## Финальная сдача

Сообщайте только важное:

- какие файлы созданы;
- какие проверки запущены;
- caveats;
- на каких слайдах еще нужны данные пользователя.
