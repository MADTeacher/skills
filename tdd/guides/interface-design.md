# Дизайн интерфейсов для тестируемости

## Принцип

Тестируемость должна быть следствием хорошего дизайна, а не причиной искусственных абстракций.

Хороший интерфейс:

- выражает доменную операцию;
- принимает явные входные данные;
- возвращает наблюдаемый результат;
- не создает внешние зависимости внутри себя;
- скрывает детали реализации;
- остается стабильным при рефакторинге.

## Принимай зависимости явно

Плохо:

```pseudocode
function checkout(cart) {
  paymentClient = createPaymentClientFromEnvironment()
  return paymentClient.charge(cart.total)
}
```

Такой код сложно тестировать, потому что он сам создает внешнюю зависимость.

Лучше:

```pseudocode
function checkout(cart, paymentClient) {
  return paymentClient.charge(cart.total)
}
```

Или через объект/контейнер приложения, если так принято в проекте.

## Возвращай результат

Плохо:

```pseudocode
function applyDiscount(cart) {
  if cart.total >= 100 {
    cart.total = cart.total * 0.9
  }
}
```

Лучше:

```pseudocode
function calculateDiscount(cart): Discount {
  if cart.total >= 100 {
    return Discount.percent(10)
  }

  return Discount.none()
}
```

Результат проще проверить, чем скрытый побочный эффект.

## Используй input object для сложных параметров

Плохо:

```pseudocode
registerUser(email, password, firstName, lastName, locale, marketingConsent)
```

Лучше:

```pseudocode
registerUser(input: RegisterUserInput)
```

Это:

- упрощает сигнатуру;
- делает тесты читаемее;
- облегчает расширение;
- позволяет валидировать данные ближе к границе.

## Предпочитай доменные результаты

Плохо:

```pseudocode
result = checkout(cart)
expect(result).toEqual(true)
```

Лучше:

```pseudocode
result = checkout(cart)
expect(result.status).toEqual("confirmed")
expect(result.receiptId).toExist()
```

Доменные результаты делают тесты выразительнее.

## Не проектируй интерфейс вокруг моков

Плохой признак: интерфейс появляется только потому, что иначе неудобно проверить, был ли вызван внутренний метод.

Лучше проверить поведение через более высокий публичный интерфейс.

Абстракция оправдана, если она отделяет систему от настоящей внешней границы:

- платежный провайдер;
- email-сервис;
- очередь сообщений;
- файловая система;
- системное время;
- генератор случайности;
- сторонний API.
