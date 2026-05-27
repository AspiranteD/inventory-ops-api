"""
Dashboard service: multi-table aggregations for inventory stats,
sales summaries, financial P&L, and daily reports.
"""
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, Protocol


class StatsRepository(Protocol):
    def count_items(self, available: Optional[bool] = None) -> int: ...
    def count_active_orders(self) -> int: ...
    def count_active_listings(self) -> int: ...
    def sum_sales(self, start: date, end: date) -> tuple[int, Decimal]: ...
    def sum_income(self, start: date, end: date) -> Decimal: ...
    def sum_expenses(self, start: date, end: date) -> Decimal: ...
    def daily_sales_detail(self, target: date) -> list[dict]: ...
    def daily_transactions_detail(self, target: date) -> list[dict]: ...
    def daily_expenses_detail(self, target: date) -> list[dict]: ...
    def daily_new_items(self, target: date) -> list[dict]: ...


@dataclass
class DashboardStats:
    period_start: date
    period_end: date
    total_items: int
    available_items: int
    sold_items: int
    availability_rate: float
    sales_count: int
    sales_total: float
    average_sale: float
    income: float
    expenses: float
    profit: float
    profit_margin: float
    pending_orders: int
    active_listings: int


class DashboardService:
    def __init__(self, repo: StatsRepository):
        self._repo = repo

    def get_stats(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> DashboardStats:
        start = start_date or (date.today() - timedelta(days=30))
        end = end_date or date.today()

        total = self._repo.count_items()
        available = self._repo.count_items(available=True)
        sold = total - available

        sales_count, sales_total = self._repo.sum_sales(start, end)
        income = self._repo.sum_income(start, end)
        expenses = self._repo.sum_expenses(start, end)
        profit = income - expenses
        profit_margin = float(profit / income * 100) if income > 0 else 0.0

        return DashboardStats(
            period_start=start,
            period_end=end,
            total_items=total,
            available_items=available,
            sold_items=sold,
            availability_rate=(available / total * 100) if total > 0 else 0,
            sales_count=sales_count,
            sales_total=float(sales_total),
            average_sale=float(sales_total / sales_count) if sales_count > 0 else 0,
            income=float(income),
            expenses=float(expenses),
            profit=float(profit),
            profit_margin=profit_margin,
            pending_orders=self._repo.count_active_orders(),
            active_listings=self._repo.count_active_listings(),
        )

    def get_daily_report(self, target: date) -> dict:
        sales = self._repo.daily_sales_detail(target)
        transactions = self._repo.daily_transactions_detail(target)
        expenses = self._repo.daily_expenses_detail(target)
        new_items = self._repo.daily_new_items(target)

        return {
            "date": target.isoformat(),
            "summary": {
                "total_sales": len(sales),
                "sales_amount": sum(s.get("final_price", 0) for s in sales),
                "total_transactions": len(transactions),
                "transactions_amount": sum(
                    t.get("amount", 0) for t in transactions
                ),
                "total_expenses": len(expenses),
                "expenses_amount": sum(e.get("total_amount", 0) for e in expenses),
                "new_items": len(new_items),
                "new_items_cost": sum(
                    i.get("purchase_price", 0) for i in new_items
                ),
            },
            "details": {
                "sales": sales,
                "transactions": transactions,
                "expenses": expenses,
                "new_items": new_items,
            },
        }
