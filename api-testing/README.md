# REST API — JSONPlaceholder

Учебная Postman-коллекция: **5 запросов и 18 проверок**. Актуальный файл — [JSONPlaceholder_API_Tests.postman_collection.json](JSONPlaceholder_API_Tests.postman_collection.json).

Исходный [ReqRes_API_Tests.postman_collection.json](ReqRes_API_Tests.postman_collection.json) оставлен для истории: несмотря на имя, его адреса ведут в JSONPlaceholder; в экспорте присутствуют две `pm.test` проверки. Скриншот [PM-collection.png](PM-collection.png) относится к исходной работе, а не к новому прогону.

| Метод | Путь | Ожидание | Дополнительная проверка |
|---|---|---|---|
| GET | /users | 200 | Массив из 10 записей, id и email |
| GET | /users/2 | 200 | id = 2, email |
| GET | /users/999 | 404 | Пустой объект |
| POST | /users | 201 | id, переданные name и email |
| DELETE | /users/1 | 200 | Пустой объект |

Все запросы проверяют Content-Type. Жёсткий SLA на время ответа учебного внешнего API не заявлен.

## Запуск

В Postman импортировать актуальный JSON, проверить `baseUrl`, выполнить Collection Runner. В Newman:

```bash
npx newman run api-testing/JSONPlaceholder_API_Tests.postman_collection.json
```

POST и DELETE у JSONPlaceholder имитируют запись: данные не сохраняются на сервере. Поэтому последующий GET не доказывает создание или удаление. Для настоящего цикла изменения данных есть [локальный Reservation Lab](../automation/README.md).

Обновлённые проверки подготовлены с помощью Codex. Статус фактического запуска — в [отчёте](../automation/verification.md). [Документация JSONPlaceholder](https://jsonplaceholder.typicode.com/guide/).
