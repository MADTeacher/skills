# Поведенческие тесты

## Принцип

Тест должен описывать поведение системы через публичный интерфейс.

Он должен отвечать на вопрос:

> Что получает пользователь, вызывающий код или внешняя система?

А не на вопрос:

> Какие внутренние функции были вызваны?

## Хороший тест

```pseudocode
test "registered user can sign in with valid credentials" {
  users = createUserService()

  users.register(email: "user@example.com", password: "correct-password")

  result = users.signIn(email: "user@example.com", password: "correct-password")

  expect(result.status).toEqual("signed_in")
  expect(result.user.email).toEqual("user@example.com")
}
```

Почему это хороший тест:

- проверяет наблюдаемое поведение;
- использует публичный интерфейс;
- не знает, где хранится пользователь;
- не утверждает порядок внутренних вызовов;
- останется полезным после внутреннего рефакторинга.

## Плохой тест

```pseudocode
test "sign in calls password hasher and repository" {
  passwordHasher = mock(PasswordHasher)
  userRepository = mock(UserRepository)
  service = SignInService(passwordHasher, userRepository)

  service.signIn("user@example.com", "correct-password")

  verify(passwordHasher.hashWasCalledOnce())
  verify(userRepository.findByEmailWasCalledOnce())
}
```

Проблема такого теста: он проверяет внутренний путь выполнения. Если реализация изменится, но поведение останется верным, тест может сломаться без реальной регрессии.

## Лучше проверять результат

```pseudocode
test "sign in rejects wrong password" {
  users = createUserService()

  users.register(email: "user@example.com", password: "correct-password")

  result = users.signIn(email: "user@example.com", password: "wrong-password")

  expect(result.status).toEqual("rejected")
  expect(result.reason).toEqual("invalid_credentials")
}
```

## Признаки хорошего теста

Хороший тест обычно:

- формулируется языком сценария;
- проверяет результат, состояние или внешний эффект;
- не зависит от приватных методов;
- не требует моков внутренних классов;
- остается зеленым при безопасном рефакторинге;
- падает при реальной поломке поведения.

## Признаки плохого теста

Плохой тест часто:

- проверяет, какой метод был вызван;
- фиксирует порядок внутренних вызовов;
- повторяет реализацию внутри теста;
- требует большого количества mock-объектов;
- ломается при переименовании или перемещении внутренних классов;
- проходит, даже если пользовательский сценарий фактически сломан.

## Формулировка имени теста

Имя теста должно описывать поведение:

Хорошо:

```text
user can reset password with a valid reset token
checkout rejects expired payment method
search returns only visible documents
```

Плохо:

```text
calls repository
runs validator
uses mapper
returns true
```
