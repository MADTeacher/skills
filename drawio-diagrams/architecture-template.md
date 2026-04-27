# Шаблон архитектурной/структурной схемы

## Пример: микросервисная архитектура

```xml
<mxfile host="app.diagrams.net">
  <diagram name="Архитектура" id="arch-1">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- Клиент -->
        <mxCell id="2" value="Клиент" style="shape=actor;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="60" y="200" width="40" height="60" as="geometry"/>
        </mxCell>

        <!-- API Gateway -->
        <mxCell id="3" value="API Gateway" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="200" y="200" width="140" height="60" as="geometry"/>
        </mxCell>

        <!-- Сервис A -->
        <mxCell id="4" value="Сервис A" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="440" y="120" width="120" height="60" as="geometry"/>
        </mxCell>

        <!-- Сервис B -->
        <mxCell id="5" value="Сервис B" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="440" y="280" width="120" height="60" as="geometry"/>
        </mxCell>

        <!-- БД A -->
        <mxCell id="6" value="БД A" style="shape=cylinder3;whiteSpace=wrap;html=1;size=15;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="650" y="110" width="80" height="80" as="geometry"/>
        </mxCell>

        <!-- БД B -->
        <mxCell id="7" value="БД B" style="shape=cylinder3;whiteSpace=wrap;html=1;size=15;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="650" y="270" width="80" height="80" as="geometry"/>
        </mxCell>

        <!-- Message Queue -->
        <mxCell id="8" value="Message&#xa;Queue" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;" vertex="1" parent="1">
          <mxGeometry x="440" y="200" width="120" height="60" as="geometry"/>
        </mxCell>

        <!-- Рёбра -->
        <mxCell id="10" value="HTTP" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="2" target="3" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="11" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="3" target="4" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="12" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="3" target="5" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="13" style="edgeStyle=orthogonalEdgeStyle;html=1;dashed=1;" edge="1" source="4" target="8" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="14" style="edgeStyle=orthogonalEdgeStyle;html=1;dashed=1;" edge="1" source="8" target="5" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="15" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="4" target="6" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="16" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="5" target="7" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Цветовая кодировка для архитектурных схем

| Элемент | fillColor | strokeColor |
|---------|-----------|-------------|
| Клиент/Пользователь | `#dae8fc` | `#6c8ebf` |
| API Gateway / Балансировщик | `#fff2cc` | `#d6b656` |
| Сервисы | `#d5e8d4` | `#82b366` |
| Базы данных | `#f8cecc` | `#b85450` |
| Очереди сообщений | `#e1d5e7` | `#9673a6` |
| Внешние системы | `#FFE6CC` | `#D79B00` |

## Полезные стили для архитектуры

### Контейнер/группа (подсистема)

```xml
<mxCell id="grp1" value="Подсистема" style="rounded=1;whiteSpace=wrap;html=1;dashed=1;fillColor=#fafafa;verticalAlign=top;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="400" height="300" as="geometry"/>
</mxCell>
<!-- Дочерние элементы с parent="grp1" -->
```

### Облако (внешняя система)

```xml
<mxCell id="ext" value="Внешний API" style="ellipse;shape=cloud;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="80" as="geometry"/>
</mxCell>
```

### Документ

```xml
<mxCell id="doc" value="Документ" style="shape=document;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

### Сервер

```xml
<mxCell id="srv" value="Сервер" style="shape=mxgraph.cisco.servers.standard_server;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="50" height="60" as="geometry"/>
</mxCell>
```
