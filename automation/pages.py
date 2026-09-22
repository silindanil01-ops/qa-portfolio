from playwright.sync_api import Page


class ReservationPage:
    def __init__(self, page: Page):
        self.page = page
        self.result = page.get_by_role("status")
        self.stock = page.locator("#stock")

    def open(self, url):
        self.page.goto(url)
        self.page.get_by_label("Товар", exact=True).select_option("TEA-001")

    def reserve(self, quantity, email="qa@example.com"):
        self.page.get_by_label("Количество").fill(str(quantity))
        self.page.get_by_label("Email", exact=True).fill(email)
        self.page.get_by_role("button", name="Зарезервировать", exact=True).click()

    def cancel(self):
        self.page.get_by_role("button", name="Отменить резерв", exact=True).click()
