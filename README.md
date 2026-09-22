# Данил Силин

**Middle QA Engineer · Mobile QA / Python Automation / API**

Белгород · удалённая работа

[Email](mailto:danil52283@mail.ru) · [Telegram](https://t.me/flatz_33) · [Резюме PDF](docs/Danil_Silin_Ozon_Job_CV.pdf) · [DOCX](docs/Danil_Silin_Ozon_Job_CV.docx)

Портфолио под роль [инженера по тестированию Ozon Job](https://getmatch.ru/vacancies/36247-inzhener-po-testirovaniiu-ozon-job): мобильный тест-дизайн Android/iOS, сценарии отказов и восстановления, тестовая документация, Python-автоматизация API и web. Начните с [соответствия требованиям вакансии](career/ozon-job-fit.md) и доказательств ниже.

## Работы и доказательства

| Проект | Что посмотреть | Артефакты |
|---|---|---|
| Mobile QA · проектирование тестов | 14 сценариев приложения смен, риски, матрица Android/iOS; дизайн без прогона на устройстве | [Мобильный раздел](mobile/README.md) · [Сценарии](mobile/test-cases.md) |
| DemoQA · ручное тестирование | 9 сценариев формы регистрации, позитивные и негативные проверки | [Тест-кейсы](test-cases/README.md) · [Qase](test-cases/qase-test-cases-list.png) |
| DemoQA · анализ дефектов | Белый экран при очистке даты и неработающее закрытие модального окна; шаги и ошибки Console | [Баг-репорты](bug-reports/README.md) |
| JSONPlaceholder · REST API | 5 запросов, проверки статусов и тела ответа на JavaScript | [Postman](api-testing/README.md) |
| Reservation Lab · автоматизация | HTTP API, UI, валидация, идемпотентность, конкурентные запросы, согласованность БД | [Проект](automation/README.md) · [Тесты](automation/tests) · [Отчёт](automation/verification.md) |
| Reservation Lab · тестовая модель | Риски, критерии приёмки, границы, связь требований и проверок | [Стратегия](manual/test-strategy.md) · [Тест-дизайн](manual/test-design.md) |

**Контекст работ:** мобильные сценарии спроектированы для условного приложения смен и пока не запускались на Android/iOS. DemoQA и JSONPlaceholder — учебная практика. Reservation Lab — учебный стенд, созданный с помощью Codex; его 36 тестов прошли локально. Коммерческие проекты в этих публичных материалах не представлены. [Отчёт прогонов](automation/verification.md).

## Подход к проверкам

- Сначала описать ожидаемое поведение и риск, затем выбирать уровень теста.
- Проверять данные и побочные эффекты, а не только HTTP-статус.
- Разделять подтверждённый дефект и вопрос к требованиям.
- Изолировать тестовые данные, сохранять отчёты и инструкции воспроизведения.

## Запустить учебные автотесты

Python 3.11 или 3.12. Команды выполняются из корня репозитория.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m playwright install chromium
python -m pytest --browser chromium --junitxml=test-results/results.xml
```

На Linux при отсутствии системных библиотек браузера: `python -m playwright install --with-deps chromium`.
Без браузера: `python -m pytest -m "api or sql"`.
Каждый тест получает новую SQLite-базу и HTTP-сервер на свободном локальном порту. Внешние сайты для этих проверок не нужны.

## Инструменты по материалам

| Направление | Инструменты | Где представлены |
|---|---|---|
| Мобильный тест-дизайн | матрица Android/iOS, офлайн, push, deep link, жизненный цикл | [Mobile QA](mobile/README.md) |
| Ручная практика | Qase, Jira, DevTools | DemoQA |
| API-практика | Postman, HTTP, JSON, JavaScript assertions | JSONPlaceholder |
| Учебная автоматизация | Python, pytest, requests, Playwright, Page Object | Reservation Lab |
| Проверка данных | SQLite, JOIN, GROUP BY, CTE, оконная функция | [SQL](automation/sql) |
| Запуск в CI | GitHub Actions, JUnit XML, Playwright trace при ошибке | [Workflow](.github/workflows/tests.yml) |

Веб-версия портфолио находится в [docs/index.html](docs/index.html). Её можно опубликовать через GitHub Pages. Инструкция по настройке Pages — в [career/START_HERE.md](career/START_HERE.md).
