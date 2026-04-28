#!/usr/bin/env node
/**
 * export_deck_pptx.mjs — экспортирует многофайловую презентацию в редактируемый PPTX
 *
 * Использование:
 *   node export_deck_pptx.mjs --slides <dir> --out <file.pptx>
 *
 * Поведение:
 *   - Вызывает scripts/html2pptx.js и переводит элементы HTML DOM в родные объекты PowerPoint
 *   - Текст становится настоящими текстовыми блоками, которые можно редактировать двойным кликом в PPT
 *   - Размер body: 960pt × 540pt (LAYOUT_WIDE, 13.333″ × 7.5″)
 *
 * ⚠️ HTML должен соблюдать 6 жестких ограничений (см. references/pptx-authoring.md):
 *   1. Текст обернут в <p>/<h1>-<h6> (нельзя класть текст прямо в div)
 *   2. CSS-градиенты не используются
 *   3. У <p>/<h*> нет background/border/shadow (выносите это на внешний div)
 *   4. У div нет background-image (используйте <img>)
 *   5. Макет измерим: явные размеры, позиции и простые grid/flex-структуры
 *   6. Эмоджи-подсказки заданы как управляемый текст или отдельный слой изображения
 *
 * HTML, написанный только ради визуальной свободы, почти никогда не пройдет проверку:
 * ограничения нужно учитывать с первой строки HTML.
 * Для задач, где важнее визуальная свобода или сложные CSS/SVG-композиции,
 * используйте export_deck_pdf.mjs / export_deck_stage_pdf.mjs и экспортируйте PDF/PNG.
 *
 * Зависимости: npm install playwright pptxgenjs sharp
 *
 * Слайды сортируются по имени файла (01-xxx.html → 02-xxx.html → ...).
 */

import pptxgen from 'pptxgenjs';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function parseArgs() {
  const args = {};
  const a = process.argv.slice(2);
  for (let i = 0; i < a.length; i += 2) {
    const k = a[i].replace(/^--/, '');
    args[k] = a[i + 1];
  }
  if (!args.slides || !args.out) {
    console.error('Использование: node export_deck_pptx.mjs --slides <dir> --out <file.pptx>');
    console.error('');
    console.error('⚠️ HTML должен соблюдать 6 жестких ограничений (см. references/pptx-authoring.md).');
    console.error('   Если важнее визуальная свобода, используйте export_deck_pdf.mjs для экспорта PDF.');
    process.exit(1);
  }
  return args;
}

async function main() {
  const { slides, out } = parseArgs();
  const slidesDir = path.resolve(slides);
  const outFile = path.resolve(out);

  const files = (await fs.readdir(slidesDir))
    .filter(f => f.endsWith('.html'))
    .sort();
  if (!files.length) {
    console.error(`В ${slidesDir} не найдены .html-файлы`);
    process.exit(1);
  }

  console.log(`Конвертируем слайды через html2pptx: ${files.length}...`);

  const { createRequire } = await import('module');
  const require = createRequire(import.meta.url);
  let html2pptx;
  try {
    html2pptx = require(path.join(__dirname, 'html2pptx.js'));
  } catch (e) {
    console.error(`✗ Не удалось загрузить html2pptx.js: ${e.message}`);
    console.error(`  Если не хватает зависимостей, запустите: npm install playwright pptxgenjs sharp`);
    process.exit(1);
  }

  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';  // 13.333 × 7.5 inch, соответствует HTML body 960 × 540 pt

  const errors = [];
  for (let i = 0; i < files.length; i++) {
    const f = files[i];
    const fullPath = path.join(slidesDir, f);
    try {
      await html2pptx(fullPath, pres);
      console.log(`  [${i + 1}/${files.length}] ${f} ✓`);
    } catch (e) {
      console.error(`  [${i + 1}/${files.length}] ${f} ✗  ${e.message}`);
      errors.push({ file: f, error: e.message });
    }
  }

  if (errors.length) {
    console.error(`\n⚠️ Не удалось конвертировать слайды: ${errors.length}. Частая причина: HTML не соблюдает 6 жестких ограничений.`);
    console.error(`  Подробнее см. раздел "частые ошибки" в references/pptx-authoring.md.`);
    if (errors.length === files.length) {
      console.error(`✗ Все слайды упали, PPTX не будет создан.`);
      process.exit(1);
    }
  }

  await pres.writeFile({ fileName: outFile });
  console.log(`\n✓ Записан файл ${outFile}  (${files.length - errors.length}/${files.length} слайдов, редактируемый PPTX)`);
}

main().catch(e => { console.error(e); process.exit(1); });
