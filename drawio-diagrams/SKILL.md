---
name: drawio-diagrams
description: Создаёт и редактирует диаграммы в формате drawio (XML) — блок-схемы алгоритмов, архитектурные и структурные схемы, sequence-диаграммы. Использовать, когда пользователь просит создать диаграмму, схему, flowchart, блок-схему, архитектурную схему, sequence-диаграмму, или упоминает drawio, .drawio, diagrams.net.
---

# DrawIO Diagrams

Создание и редактирование диаграмм в формате `.drawio` (XML).

## Формат файла

DrawIO использует XML-формат. Базовая структура:

```xml
<mxfile>
  <diagram name="Название" id="unique-id">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- элементы диаграммы -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Идентификаторы

- `id` — уникальный идентификатор ячейки (строка)
- `parent` — ссылка на родителя (`"1"` — корневой слой)
- `source` / `target` — начальная/конечная ячейка для рёбер
- Начинать нумерацию с `2` (0 и 1 зарезервированы)

## Координаты и размеры

- `x`, `y` — позиция левого верхнего угла (в пикселях)
- `width`, `height` — размеры (в пикселях)
- Стандартный размер прямоугольника: `width="120" height="60"`
- Отступы между элементами: минимум `40px` по горизонтали, `60px` по вертикали

## Типы элементов

### Прямоугольник (процесс/действие)

```xml
<mxCell id="2" value="Действие" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

### Скруглённый прямоугольник (начало/конец)

```xml
<mxCell id="2" value="Начало" style="rounded=1;whiteSpace=wrap;html=1;arcSize=50;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

### Ромб (условие)

```xml
<mxCell id="3" value="Условие?" style="rhombus;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="80" y="200" width="160" height="80" as="geometry"/>
</mxCell>
```

### Параллелограмм (ввод/вывод)

```xml
<mxCell id="4" value="Ввод данных" style="shape=parallelogram;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="90" y="100" width="140" height="60" as="geometry"/>
</mxCell>
```

### Овал (начало/конец — альтернатива)

```xml
<mxCell id="2" value="Старт" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="120" y="100" width="80" height="50" as="geometry"/>
</mxCell>
```

### Цилиндр (база данных)

```xml
<mxCell id="5" value="БД" style="shape=cylinder3;whiteSpace=wrap;html=1;size=15;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="80" height="80" as="geometry"/>
</mxCell>
```

### Компонент (UML-компонент)

```xml
<mxCell id="6" value="Сервис" style="html=1;dropTarget=0;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

### Рёбра (связи)

**Прямая стрелка:**

```xml
<mxCell id="10" style="edgeStyle=none;html=1;" edge="1" source="2" target="3" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

**Стрелка с подписью:**

```xml
<mxCell id="10" value="Да" style="edgeStyle=none;html=1;" edge="1" source="3" target="4" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

**Ортогональная стрелка (прямые углы):**

```xml
<mxCell id="10" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="2" target="3" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

## Стили (быстрый справочник)

| Стиль | Назначение |
|-------|-----------|
| `rounded=0` | Прямоугольник с прямыми углами |
| `rounded=1;arcSize=50` | Скруглённый (терминатор) |
| `rhombus` | Ромб (условие) |
| `ellipse` | Овал |
| `shape=parallelogram` | Параллелограмм |
| `shape=cylinder3;size=15` | Цилиндр (БД) |
| `shape=hexagon` | Шестиугольник (цикл) |
| `dashed=1` | Пунктирная линия |
| `strokeColor=#FF0000` | Цвет границы |
| `fillColor=#FFFFFF` | Цвет заливки |
| `fontColor=#000000` | Цвет текста |
| `fontSize=14` | Размер шрифта |
| `fontStyle=1` | Жирный (0=обычный, 2=курсив, 3=жирный+курсив) |
| `edgeStyle=orthogonalEdgeStyle` | Ортогональные рёбра |
| `edgeStyle=elbowEdgeStyle` | Ломаные рёбра |
| `curved=1` | Скруглённые рёбра |
| `entryX=0.5;entryY=0` | Точка входа (центр-верх) |
| `exitX=0.5;exitY=1` | Точка выхода (центр-низ) |

## Шаблоны диаграмм

### Блок-схема алгоритма

Подробный шаблон — см. [flowchart-template.md](flowchart-template.md).

### Архитектурная схема

Подробный шаблон — см. [architecture-template.md](architecture-template.md).

### Sequence-диаграмма

Подробный шаблон — см. [sequence-template.md](sequence-template.md).

## Правила создания диаграмм

1. **Автоматическая нумерация**: id элементов — возрастающие числа (`"2"`, `"3"`, `"4"`...)
2. **Читаемость**: между элементами минимум `40px` по горизонтали и `60px` по вертикали
3. **Выравнивание**: центрировать элементы по общей оси
4. **Подписи рёбер**: для условий всегда указывать `"Да"` / `"Нет"`
5. **Компактность**: не оставлять избыточных пустых пространств
6. **XML-экранирование**: использовать `&amp;`, `&lt;`, `&gt;`, `&quot;` вместо `&`, `<`, `>`, `"`

## Рабочий процесс

1. Определить тип диаграммы из запроса пользователя
2. Составить список элементов и связей
3. Рассчитать координаты (сверху вниз или слева направо)
4. Сгенерировать XML и записать в `.drawio`-файл
5. Сообщить пользователю путь к файлу

### Расчёт компоновки (сверху вниз)

```
y_position = start_y + (element_index * (element_height + gap))
x_center   = page_width / 2 - element_width / 2
```

Типичные значения:
- `start_y = 40`
- `gap = 40` (между элементами)
- `page_width = 800`
