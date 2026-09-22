# Тест-дизайн и трассировка

Проверки спроектированы по правилам учебного сервиса. Фактический результат — в [отчёте](../automation/verification.md).

## Количество товара

| Класс или граница | Данные | Ожидаемый результат |
|---|---|---|
| Меньше минимума | -1, 0 | 422, остаток не меняется |
| Минимум | 1 | 201 при наличии |
| Ровно остаток | 10 | 201, остаток 0 |
| Больше остатка | 11 | 409, остаток 10 |
| Максимум диапазона | 100 | Диапазон допустим, но при остатке 10 — 409 |
| Выше диапазона | 101 | 422 |
| Неверный тип | 1.5, "2", true, null | 422 |

Валидация диапазона и ограничение остатка проверяются отдельно. JSON boolean не считается integer даже при особенностях типов Python.

## Таблица решений для повторного запроса

| Ключ уже есть | Данные совпадают | Состояние | Результат |
|---|---|---|---|
| Нет | — | — | Новый резерв, 201 |
| Да | Да | active | Старый резерв, 200, без списания |
| Да | Да | cancelled | Старый cancelled, 200, без активации |
| Да | Нет | Любое | 409, без изменения данных |

## Требования и тесты

| Требования | Проверки |
|---|---|
| R-01, R-02, R-04 | test_create_read_and_stock_contract, test_quantity_boundaries_and_business_limit |
| R-02, R-03, R-07 | test_invalid_quantity_does_not_change_stock, test_invalid_email, test_bad_payload, test_key_required, test_unknown_product |
| R-05, R-06 | test_replay_does_not_reserve_twice, test_same_key_different_payload_is_conflict |
| R-08, R-09 | test_cancel_is_idempotent, test_replay_after_cancel_does_not_reactivate |
| R-10 | test_parallel_requests_cannot_oversell, test_join_aggregation_preserves_inventory_invariant |
| R-11 | test_unknown_reservation |
| R-12 | test_reserve_and_cancel_in_browser, test_insufficient_stock_shows_business_error, test_network_failure_can_be_retried |

Таблица показывает выбранные проверки, не полное покрытие всех вариантов требований. Границы длины email и ключа пока оставлены для исследовательской сессии.
