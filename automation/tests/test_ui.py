import pytest
from playwright.sync_api import expect

from automation.pages import ReservationPage

pytestmark = pytest.mark.ui


def test_reserve_and_cancel_in_browser(page, lab, api):
    form = ReservationPage(page)
    form.open(lab.url)
    expect(form.stock).to_have_text("Доступно: 10")
    form.reserve(2)
    expect(form.result).to_have_text("Резерв создан: 2 шт.")
    expect(form.stock).to_have_text("Доступно: 8")
    assert api.stock() == 8
    form.cancel()
    expect(form.result).to_have_text("Резерв отменён")
    expect(form.stock).to_have_text("Доступно: 10")
    assert api.stock() == 10


def test_insufficient_stock_shows_business_error(page, lab, api):
    form = ReservationPage(page)
    form.open(lab.url)
    form.reserve(11)
    expect(form.result).to_have_text("Недостаточно товара")
    expect(form.stock).to_have_text("Доступно: 10")
    expect(page.get_by_role("button", name="Зарезервировать", exact=True)).to_be_enabled()
    assert api.stock() == 10


def test_required_email_blocks_submission(page, lab, api):
    form = ReservationPage(page)
    form.open(lab.url)
    form.reserve(2, email="")
    assert page.get_by_label("Email", exact=True).evaluate("el => el.validity.valueMissing")
    expect(form.result).to_have_text("")
    assert api.stock() == 10


def test_network_failure_can_be_retried(page, lab, api):
    form = ReservationPage(page)
    form.open(lab.url)
    page.route("**/api/reservations", lambda route: route.abort())
    form.reserve(2)
    expect(form.result).to_have_text("Ошибка соединения. Повторите запрос.")
    expect(page.get_by_role("button", name="Зарезервировать", exact=True)).to_be_enabled()
    assert api.stock() == 10
    page.unroute("**/api/reservations")
    form.reserve(2)
    expect(form.result).to_have_text("Резерв создан: 2 шт.")
    assert api.stock() == 8
