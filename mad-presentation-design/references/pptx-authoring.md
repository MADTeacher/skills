# PPTX authoring

Редактируемый PPTX — это перевод HTML-объектов в PowerPoint-объекты, а не
скриншот. Исходный HTML должен быть constrained с самого начала.

## Размер

Используйте:

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

Это соответствует PowerPoint wide.

## Жесткие ограничения

### 1. Текст — только в семантических текстовых тегах

Текст должен быть в `p`, headings, `ul` или `ol`, а не напрямую внутри `div`.

```html
<!-- Плохо -->
<div>Total revenue</div>

<!-- Хорошо -->
<div class="label"><p>Total revenue</p></div>
```

### 2. Визуальные контейнеры отдельно от текста

Background, border и shadow должны быть на контейнере `div`. Текстовые теги
держат текст.

### 3. Избегайте CSS без аналога в PPTX

Не используйте gradients, filters, complex masks и unsupported blend modes в
редактируемых слайдах. Если эффект обязателен, рендерьте его как image layer, а
текст рядом оставляйте editable.

### 4. Изображения через `img`

Не полагайтесь на `background-image` для объектов, которые должны появиться в
PPTX.

```html
<img class="hero" src="hero.png" alt="" />
```

### 5. Layout должен быть измеримым

Используйте явные размеры, позиции и простые grid/flex-структуры. Проверяйте,
что контент не выходит за body.

## Рекомендуемый skeleton

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

1. Решите, что PPTX нужен, до глубокой визуальной проработки.
2. Соберите слайды как constrained HTML.
3. Проверьте HTML в браузере.
4. Запустите:

```bash
node scripts/export_deck_pptx.mjs --slides deck/slides --out deck.pptx
```

5. Откройте PPTX и проверьте:
   - текст редактируется;
   - изображения на месте;
   - объекты не выходят за слайд;
   - визуальные упрощения приемлемы.

## Существующий богатый HTML

Если исходный дек использует сложные browser-only эффекты, не обещайте
идеальный editable PPTX. Создайте constrained PPTX-версию и, если полезно,
отдайте рядом faithful PDF/PNG.

## Частые ошибки

- Текст напрямую внутри `div`.
- Контент выходит за body.
- Визуальный эффект стоит на текстовом теге.
- `background-image` на `div`.
- PowerPoint подменяет шрифты иначе, чем браузер.
- Слишком тесные text boxes.

Editable export — это дизайн-ограничение, а не последний шаг.
