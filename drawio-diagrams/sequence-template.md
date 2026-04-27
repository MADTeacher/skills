# Шаблон Sequence-диаграммы

Sequence-диаграммы в drawio используют стандартные прямоугольники для участников и рёбра с точками входа/выхода для сообщений.

## Пример: взаимодействие сервисов

```xml
<mxfile host="app.diagrams.net">
  <diagram name="Sequence" id="seq-1">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- Участники -->
        <mxCell id="2" value="Клиент" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="100" y="40" width="100" height="40" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="Сервер" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="350" y="40" width="100" height="40" as="geometry"/>
        </mxCell>
        <mxCell id="4" value="БД" style="shape=cylinder3;whiteSpace=wrap;html=1;size=10;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="600" y="30" width="80" height="60" as="geometry"/>
        </mxCell>

        <!-- Линии жизни (вертикальные) -->
        <mxCell id="5" style="endArrow=none;dashed=1;html=1;" edge="1" parent="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="150" y="80" as="sourcePoint"/>
            <mxPoint x="150" y="500" as="targetPoint"/>
          </mxGeometry>
        </mxCell>
        <mxCell id="6" style="endArrow=none;dashed=1;html=1;" edge="1" parent="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="400" y="80" as="sourcePoint"/>
            <mxPoint x="400" y="500" as="targetPoint"/>
          </mxGeometry>
        </mxCell>
        <mxCell id="7" style="endArrow=none;dashed=1;html=1;" edge="1" parent="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="640" y="90" as="sourcePoint"/>
            <mxPoint x="640" y="500" as="targetPoint"/>
          </mxGeometry>
        </mxCell>

        <!-- Сообщения -->
        <!-- 1. Запрос -->
        <mxCell id="10" value="1. POST /api/data" style="html=1;verticalAlign=bottom;endArrow=block;" edge="1" parent="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="150" y="130" as="sourcePoint"/>
            <mxPoint x="400" y="130" as="targetPoint"/>
          </mxGeometry>
        </mxCell>

        <!-- 2. Query -->
        <mxCell id="11" value="2. SELECT" style="html=1;verticalAlign=bottom;endArrow=block;" edge="1" parent="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="400" y="190" as="sourcePoint"/>
            <mxPoint x="640" y="190" as="targetPoint"/>
          </mxGeometry>
        </mxCell>

        <!-- 3. Result -->
        <mxCell id="12" value="3. Результат" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;" edge="1" parent="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="640" y="240" as="sourcePoint"/>
            <mxPoint x="400" y="240" as="targetPoint"/>
          </mxGeometry>
        </mxCell>

        <!-- 4. Response -->
        <mxCell id="13" value="4. 200 OK" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;" edge="1" parent="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="400" y="290" as="sourcePoint"/>
            <mxPoint x="150" y="290" as="targetPoint"/>
          </mxGeometry>
        </mxCell>

        <!-- 5. Self-call (цикл на сервере) -->
        <mxCell id="14" value="5. Валидация" style="html=1;verticalAlign=bottom;endArrow=block;" edge="1" parent="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="400" y="150" as="sourcePoint"/>
            <mxPoint x="430" y="170" as="targetPoint"/>
            <Array as="points">
              <mxPoint x="430" y="150"/>
            </Array>
          </mxGeometry>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Правила для sequence-диаграмм

### Сообщения

| Тип | Стиль | Когда использовать |
|------|-------|-------------------|
| Синхронный вызов | `endArrow=block;` | Обычный запрос |
| Асинхронный вызов | `endArrow=open;` | Отправка без ожидания |
| Ответ | `endArrow=open;dashed=1;` | Возврат результата |
| Self-call | см. пример "Валидация" | Внутренний вызов |

### Координаты

- Участники располагаются по горизонтали с шагом `250px`
- Сообщения располагаются по вертикали с шагом `60px`
- Первое сообщение на `y=130` (с учётом шапки участников)
- Линия жизни: от `y = (участник.y + участник.height)` до `y = (последнее_сообщение.y + 60)`

### Подписи

- Нумерация: `1.`, `2.`, `3.`...
- Формат подписи: `<number>. <action>`
- Для ответов использовать пунктир (`dashed=1`)
