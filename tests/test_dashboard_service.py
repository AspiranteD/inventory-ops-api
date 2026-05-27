"""Tests for DashboardService."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from src.services.dashboard_service import DashboardService, DashboardStats


class FakeStatsRepo:
    def __init__(self):
        self.total_items = 100
        self.available_items = 70
        self.active_orders = 5
        self.active_listings = 80
        self.sales_count = 10
        self.sales_total = Decimal("1500")
        self.income = Decimal("2000")
        self.expenses_val = Decimal("800")
        self._daily_sales = []
        self._daily_transactions = []
        self._daily_expenses = []
        self._daily_new_items = []

    def count_items(self, available=None):
        if available is True:
            return self.available_items
        return self.total_items

    def count_active_orders(self):
        return self.active_orders

    def count_active_listings(self):
        return self.active_listings

    def sum_sales(self, start, end):
        return self.sales_count, self.sales_total

    def sum_income(self, start, end):
        return self.income

    def sum_expenses(self, start, end):
        return self.expenses_val

    def daily_sales_detail(self, target):
        return self._daily_sales

    def daily_transactions_detail(self, target):
        return self._daily_transactions

    def daily_expenses_detail(self, target):
        return self._daily_expenses

    def daily_new_items(self, target):
        return self._daily_new_items


@pytest.fixture
def svc():
    repo = FakeStatsRepo()
    return DashboardService(repo), repo


def test_stats_basic(svc):
    service, repo = svc
    stats = service.get_stats()
    assert stats.total_items == 100
    assert stats.available_items == 70
    assert stats.sold_items == 30
    assert stats.availability_rate == 70.0
    assert stats.sales_count == 10
    assert stats.sales_total == 1500.0
    assert stats.average_sale == 150.0
    assert stats.income == 2000.0
    assert stats.expenses == 800.0
    assert stats.profit == 1200.0
    assert stats.profit_margin == pytest.approx(60.0)
    assert stats.pending_orders == 5
    assert stats.active_listings == 80


def test_stats_custom_period(svc):
    service, _ = svc
    stats = service.get_stats(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )
    assert stats.period_start == date(2026, 1, 1)
    assert stats.period_end == date(2026, 1, 31)


def test_stats_zero_items(svc):
    service, repo = svc
    repo.total_items = 0
    repo.available_items = 0
    stats = service.get_stats()
    assert stats.availability_rate == 0


def test_stats_zero_sales(svc):
    service, repo = svc
    repo.sales_count = 0
    repo.sales_total = Decimal("0")
    stats = service.get_stats()
    assert stats.average_sale == 0


def test_stats_zero_income(svc):
    service, repo = svc
    repo.income = Decimal("0")
    stats = service.get_stats()
    assert stats.profit_margin == 0


def test_daily_report(svc):
    service, repo = svc
    repo._daily_sales = [
        {"id": 1, "final_price": 50.0},
        {"id": 2, "final_price": 75.0},
    ]
    repo._daily_new_items = [
        {"lpn": "A", "purchase_price": 20.0},
    ]
    report = service.get_daily_report(date.today())
    assert report["summary"]["total_sales"] == 2
    assert report["summary"]["sales_amount"] == 125.0
    assert report["summary"]["new_items"] == 1
    assert report["summary"]["new_items_cost"] == 20.0


def test_daily_report_empty(svc):
    service, _ = svc
    report = service.get_daily_report(date.today())
    assert report["summary"]["total_sales"] == 0
    assert report["details"]["sales"] == []


def test_daily_report_date_format(svc):
    service, _ = svc
    report = service.get_daily_report(date(2026, 3, 15))
    assert report["date"] == "2026-03-15"
