# Шаблон блок-схемы алгоритма

## Пример: алгоритм с условием и циклом

```xml
<mxfile host="app.diagrams.net">
  <diagram name="Блок-схема" id="flowchart-1">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- Начало -->
        <mxCell id="2" value="Начало" style="rounded=1;whiteSpace=wrap;html=1;arcSize=50;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="340" y="40" width="120" height="50" as="geometry"/>
        </mxCell>

        <!-- Ввод данных -->
        <mxCell id="3" value="Ввод данных" style="shape=parallelogram;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="320" y="130" width="160" height="50" as="geometry"/>
        </mxCell>

        <!-- Процесс -->
        <mxCell id="4" value="Обработка" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="340" y="220" width="120" height="60" as="geometry"/>
        </mxCell>

        <!-- Условие -->
        <mxCell id="5" value="Условие?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="310" y="320" width="180" height="80" as="geometry"/>
        </mxCell>

        <!-- Действие «Да» -->
        <mxCell id="6" value="Действие A" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="140" y="440" width="120" height="60" as="geometry"/>
        </mxCell>

        <!-- Действие «Нет» -->
        <mxCell id="7" value="Действие B" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="540" y="440" width="120" height="60" as="geometry"/>
        </mxCell>

        <!-- Слияние -->
        <mxCell id="8" value="" style="ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="385" y="540" width="30" height="30" as="geometry"/>
        </mxCell>

        <!-- Конец -->
        <mxCell id="9" value="Конец" style="rounded=1;whiteSpace=wrap;html=1;arcSize=50;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="340" y="620" width="120" height="50" as="geometry"/>
        </mxCell>

        <!-- Рёбра -->
        <mxCell id="10" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="2" target="3" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="11" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="3" target="4" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="12" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="4" target="5" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="13" value="Да" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="5" target="6" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="14" value="Нет" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="5" target="7" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="15" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="6" target="8" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="16" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="7" target="8" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="17" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="8" target="9" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Цветовая кодировка (рекомендуемая)

| Элемент | fillColor | strokeColor |
|---------|-----------|-------------|
| Начало/Конец | `#d5e8d4` | `#82b366` |
| Ввод/Вывод | `#dae8fc` | `#6c8ebf` |
| Процесс | `#FFFFFF` | `#000000` |
| Условие | `#fff2cc` | `#d6b656` |
| Ошибка | `#f8cecc` | `#b85450` |
| Подпроцесс | `#e1d5e7` | `#9673a6` |

## Конфигурация mxGraphModel

Рекомендуемые атрибуты:

```xml
<mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169">
```
