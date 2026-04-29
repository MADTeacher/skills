# Создание редактируемого PPTX

Редактируемый PPTX - это перевод HTML-объектов в объекты PowerPoint, а не скриншот. Поэтому исходный HTML с самого начала должен быть ограниченным (`constrained`): с понятными размерами, позициями и простыми правилами верстки.

Редактируемый PPTX здесь означает кроссплатформенный PowerPoint-совместимый результат для Windows/macOS, а не просто HTML, который хорошо выглядит в локальном браузере.

## Размер

Используй:

```css
body {
  width: 960pt;
  height: 540pt;
  margin: 0;
}

.slide {
  width: 960pt;
  height: 540pt;
  position: relative;
  overflow: hidden;
}
```

Это соответствует широкому формату PowerPoint.

## Жесткие ограничения

### 0. Кроссплатформенная текстовая безопасность обязательна

Для editable PPTX используй только такие primary text fonts:

- `Arial`
- `Verdana`
- `Trebuchet MS`
- `Georgia`
- `Times New Roman`
- `Courier New`

Рекомендуемые роли:

- sans: `Arial`
- serif: `Georgia` или `Times New Roman`
- mono: `Courier New`

Не используй как primary text font:

- `Avenir`
- `Avenir Next`
- `SF Pro`
- `San Francisco`
- `Helvetica Neue`
- `Inter`
- `-apple-system`
- `system-ui`
- `BlinkMacSystemFont`
- `Segoe UI`
- `Calibri`
- `Aptos`
- локальный или брендовый шрифт без честного принятия непаритета или без перевода такого слоя в растр

Каждый PPTX-safe HTML-слайд обязан объявлять:

```html
<meta charset="utf-8" />
```

### 1. Текст - только в семантических текстовых тегах

Текст должен быть в `p`, заголовочных тегах (`headings`), `ul` или `ol`, а не напрямую внутри `div`.

```html
<!-- Плохо -->
<div>Total revenue</div>

<!-- Хорошо -->
<div class="label"><p>Total revenue</p></div>
```

### 2. Визуальные контейнеры отдельно от текста

Фон (`background`), рамка (`border`) и тень (`shadow`) должны быть на контейнере `div`. Текстовые теги держат только текст.

### 3. Избегай CSS без аналога в PPTX

Не используй градиенты (`gradients`), фильтры (`filters`), сложные маски (`complex masks`) и неподдерживаемые режимы смешивания (`unsupported blend modes`) в редактируемых слайдах. Если эффект обязателен, отрисуй его как слой с картинкой (`image layer`), а текст рядом оставь редактируемым (`editable`).

### 4. Изображения через `img`

Не полагайся на `background-image` для объектов, которые должны появиться в PPTX.

```html
<img class="hero" src="hero.png" alt="" />
```

### 5. Верстка должна быть измеримой

Используй явные размеры, позиции и простые структуры grid/flex. Проверяй, что контент не выходит за границы `body`.

### 6. Эмоджи - не как editable text, а как слой-картинка (`image layer`) или plain text

Для PPTX-safe режима editable emoji text запрещен: его вид и метрики слишком зависят от ОС, набора шрифтов и PowerPoint. Если нужен такой cue:

- экспортируй его как маленький PNG/WebP/SVG asset;
- или замени plain-text/иконографикой рядом с редактируемым текстом.

## Рекомендуемый каркас (`skeleton`)

```html
<section class="slide">
  <div class="panel">
    <h1>Title</h1>
    <p>Body text</p>
  </div>
  <img class="hero" src="hero.png" alt="" />
</section>
```

## Процесс

1. Реши, что PPTX нужен, до глубокой визуальной проработки.
2. Работай внутри отдельной директории презентации с локальным Node/npm.
3. Скопируй весь каталог `scripts/` навыка в `scripts/` этой презентации.
4. Собери слайды как ограниченный HTML (`constrained HTML`), то есть HTML с заранее заданными размерами и простыми ограничениями.
5. Экспортируй все слайды в PNG и исправь визуальные дефекты:

```bash
node scripts/export_deck_png.mjs --slides slides --out exports/png
```

6. После чистой PNG-проверки запусти PPTX-экспорт:

```bash
node scripts/export_deck_pptx.mjs --slides slides --out exports/deck.pptx
```

7. Проверь PPTX:
   - текст редактируется;
   - первичные шрифты безопасны для Windows/macOS;
   - изображения на месте;
   - editable emoji text отсутствует;
   - `<meta charset="utf-8" />` был у каждого HTML-слайда;
   - объекты не выходят за слайд;
   - визуальные упрощения приемлемы.

## Существующий богатый HTML

Если исходная презентация использует сложные эффекты, которые работают только в браузере, не обещай идеальный редактируемый PPTX (`editable PPTX`). Создай отдельную ограниченную PPTX-версию (`constrained PPTX`), то есть версию с понятными ограничениями для экспорта в PowerPoint. Если полезно, отдай рядом точные PDF/PNG (`faithful PDF/PNG`), то есть файлы, которые лучше сохраняют внешний вид.

## Частые ошибки

- Текст напрямую внутри `div`.
- Контент выходит за границы `body`.
- Визуальный эффект висит на текстовом теге.
- `background-image` задан на `div` для важной картинки.
- PowerPoint подменяет шрифты иначе, чем браузер.
- В PPTX оставили editable emoji text и получили разный рендер на разных ОС.
- У HTML-слайда нет `<meta charset="utf-8" />`.
- Слишком тесные текстовые блоки (`text boxes`).

Редактируемый экспорт (`editable export`) - это ограничение дизайна, а не последний шаг.
