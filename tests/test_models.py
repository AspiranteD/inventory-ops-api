from datetime import datetime, date

from sqlmodel import Session

from src.models.item import PhysicalItem
from src.models.order import Order, OrderItem
from src.models.listing import Listing
from src.models.sale import Sale


class TestPhysicalItemModel:
    def test_create_item(self, session: Session):
        item = PhysicalItem(lpn="TEST-001", asin="B0TEST123", condition="new")
        session.add(item)
        session.commit()

        db_item = session.get(PhysicalItem, "TEST-001")
        assert db_item is not None
        assert db_item.asin == "B0TEST123"
        assert db_item.available is True
        assert db_item.scraping_attempts == 0

    def test_item_defaults(self, session: Session):
        item = PhysicalItem(lpn="TEST-DEF")
        session.add(item)
        session.commit()

        db_item = session.get(PhysicalItem, "TEST-DEF")
        assert db_item.available is True
        assert db_item.scraping_attempts == 0
        assert db_item.asin is None

    def test_item_with_prices(self, session: Session):
        item = PhysicalItem(
            lpn="TEST-PRICE",
            scraped_price=45.99,
            sale_price=39.99,
        )
        session.add(item)
        session.commit()

        db_item = session.get(PhysicalItem, "TEST-PRICE")
        assert db_item.scraped_price == 45.99
        assert db_item.sale_price == 39.99


class TestOrderModel:
    def test_create_order(self, session: Session):
        order = Order(
            request_id="ORD-TEST-001",
            account_id="ACC-01",
            buyer_name="Test Buyer",
            order_date=date(2024, 3, 15),
            status_id=1,
        )
        session.add(order)
        session.commit()

        db_order = session.get(Order, "ORD-TEST-001")
        assert db_order is not None
        assert db_order.buyer_name == "Test Buyer"
        assert db_order.active is True

    def test_order_with_items(self, session: Session):
        item = PhysicalItem(lpn="ITEM-FOR-ORDER", condition="new")
        session.add(item)
        session.commit()

        order = Order(request_id="ORD-REL-001", status_id=1)
        session.add(order)
        session.commit()

        order_item = OrderItem(
            request_id="ORD-REL-001",
            lpn="ITEM-FOR-ORDER",
            price=20.00,
        )
        session.add(order_item)
        session.commit()

        db_order = session.get(Order, "ORD-REL-001")
        assert len(db_order.items) == 1
        assert db_order.items[0].lpn == "ITEM-FOR-ORDER"
        assert db_order.items[0].price == 20.00


class TestListingModel:
    def test_create_listing(self, session: Session):
        listing = Listing(
            lpn="LST-TEST-001",
            platform="wallapop",
            title="Test Listing",
            sale_price=25.00,
        )
        session.add(listing)
        session.commit()

        db_listing = session.get(Listing, "LST-TEST-001")
        assert db_listing is not None
        assert db_listing.platform == "wallapop"
        assert db_listing.is_sold is False
        assert db_listing.views_count == 0

    def test_listing_counters(self, session: Session):
        listing = Listing(
            lpn="LST-COUNT",
            views_count=100,
            favorites_count=10,
            conversations_count=3,
        )
        session.add(listing)
        session.commit()

        db_listing = session.get(Listing, "LST-COUNT")
        assert db_listing.views_count == 100
        assert db_listing.favorites_count == 10


class TestSaleModel:
    def test_create_sale(self, session: Session):
        item = PhysicalItem(lpn="SALE-ITEM-001")
        session.add(item)
        session.commit()

        sale = Sale(
            lpn="SALE-ITEM-001",
            account_id="ACC-01",
            final_price=30.00,
            shipping_cost=5.00,
            platform_fee=3.00,
            sale_date=datetime(2024, 3, 20, 14, 30),
            payment_status_id=2,
        )
        session.add(sale)
        session.commit()
        session.refresh(sale)

        assert sale.id is not None
        assert sale.final_price == 30.00
        assert sale.shipping_cost == 5.00
        assert sale.platform_fee == 3.00
