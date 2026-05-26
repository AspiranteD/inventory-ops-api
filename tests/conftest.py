import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.deps import get_db
from src.models import PhysicalItem, Order, OrderItem, Listing, Sale  # noqa: F401


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    def get_db_override():
        yield session

    app = create_app()
    app.dependency_overrides[get_db] = get_db_override
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_items(session):
    items = [
        PhysicalItem(
            lpn="LPN001",
            asin="B08N5WRWNW",
            amazon_description="Wireless Mouse",
            sale_price=25.99,
            condition="new",
            available=True,
            truckload_id="TRUCK-01",
        ),
        PhysicalItem(
            lpn="LPN002",
            asin="B08N5WRWNW",
            amazon_description="Wireless Mouse (2nd)",
            sale_price=22.50,
            condition="used_good",
            available=True,
            truckload_id="TRUCK-01",
        ),
        PhysicalItem(
            lpn="LPN003",
            asin="B09XYZ1234",
            amazon_description="USB Hub",
            sale_price=15.00,
            condition="new",
            available=False,
            truckload_id="TRUCK-02",
        ),
    ]
    for item in items:
        session.add(item)
    session.commit()
    return items


@pytest.fixture
def sample_orders(session, sample_items):
    from datetime import date

    order = Order(
        request_id="ORD-001",
        account_id="ACC-01",
        buyer_name="John Doe",
        buyer_country="US",
        order_date=date(2024, 1, 15),
        status_id=1,
        active=True,
    )
    session.add(order)
    session.commit()

    order_item = OrderItem(
        request_id="ORD-001",
        lpn="LPN001",
        price=25.99,
        web_url="https://example.com/item/1",
    )
    session.add(order_item)

    order2 = Order(
        request_id="ORD-002",
        account_id="ACC-02",
        buyer_name="Jane Smith",
        buyer_country="ES",
        order_date=date(2024, 2, 20),
        status_id=2,
        active=True,
    )
    session.add(order2)
    session.commit()

    return [order, order2]


@pytest.fixture
def sample_listings(session):
    listings = [
        Listing(
            lpn="LST001",
            account_id="ACC-01",
            title="Wireless Mouse - New",
            sale_price=29.99,
            platform="wallapop",
            views_count=150,
            favorites_count=12,
            conversations_count=3,
            is_sold=False,
        ),
        Listing(
            lpn="LST002",
            account_id="ACC-01",
            title="USB Hub 4-port",
            sale_price=18.00,
            platform="wallapop",
            views_count=80,
            favorites_count=5,
            conversations_count=1,
            is_sold=True,
        ),
        Listing(
            lpn="LST003",
            account_id="ACC-02",
            title="Keyboard Mechanical",
            sale_price=45.00,
            platform="vinted",
            views_count=200,
            favorites_count=20,
            conversations_count=5,
            is_sold=False,
            is_reserved=True,
        ),
    ]
    for listing in listings:
        session.add(listing)
    session.commit()
    return listings
