# Отчёт проверки

Дата: 22 сентября 2026 года. Это локальная проверка подготовленного пакета, а не результат GitHub Actions и не оценка квалификации владельца репозитория.

| Набор | Результат | Доказательство |
|---|---|---|
| HTTP API | 29 passed | pytest-results.xml |
| SQL | 3 passed | pytest-results.xml |
| UI Chromium | 4 passed | pytest-results.xml |
| Все pytest | **36 passed, 0 failed, 0 errors**, 2.510 с | [JUnit XML](evidence/pytest-results.xml) |
| Postman через Newman | 5 запросов, **18 assertions passed**, 0 failed | [JSON summary](evidence/postman-summary.json) |
| Страница портфолио | Визуально проверена при 1440 px и 390 px; горизонтального переполнения нет | Локальный Chromium |
| Резюме DOCX | Одна страница, рендеринг и визуальная проверка выполнены | docs/Danil_Silin_Ozon_Job_CV.docx и PDF |

## Окружение

Linux, Python 3.12.14; pytest 9.1.1; pytest-playwright 0.9.0; Playwright Python 1.63.0; Chromium 153.0.8010.0. Точные Python-зависимости — requirements-lock.txt. Для этой среды использован установленный отдельно Chromium через QA_BROWSER_EXECUTABLE; штатная загрузка браузера Playwright здесь не завершилась.

Команда набора:

```bash
python -m pytest --browser chromium --tracing retain-on-failure --screenshot only-on-failure --junitxml=automation/evidence/pytest-results.xml
```

В среде проверки дополнительно заданы QA_BROWSER_EXECUTABLE (путь к локальному Chromium) и PLAYWRIGHT_NODEJS_PATH (путь к доступному Node). Эти пути зависят от машины и не захардкожены в репозитории. Обычная установка браузера описана в README.

Команда API-коллекции:

```bash
newman run api-testing/JSONPlaceholder_API_Tests.postman_collection.json --timeout-request 10000
```

Первоначальные проверки выявили неверный путь SQL-файлов и отсутствие доступного браузера. Путь исправлен, браузер настроен, затем весь набор запущен успешно. Из XML удалён только технический hostname. JSON Postman содержит извлечённые результаты без сетевых заголовков.

## Что не проверено

Python 3.11, Windows, Firefox/WebKit и фактическое выполнение workflow на GitHub не запускались. Новая ручная проверка внешнего DemoQA не проводилась. Доступность ссылок на добавленные файлы на GitHub появится после их загрузки. GitHub Pages ещё не опубликован.

Проверки Postman выполнены на внешнем учебном API; POST/DELETE имитируют изменения, а не сохраняют их. UI-проверки относятся к локальному веб-стенду и не подтверждают нативное мобильное тестирование.
