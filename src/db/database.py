from sqlmodel import SQLModel, Session, create_engine

from src.models import PhysicalItem, Order, OrderItem, Listing, Sale  # noqa: F401

DATABASE_URL = "postgresql://user:pass@localhost:5432/inventory"

engine = create_engine(DATABASE_URL, echo=False)


def get_engine(url: str | None = None):
    global engine
    if url:
        engine = create_engine(url, echo=False)
    return engine


def init_db(url: str | None = None):
    eng = get_engine(url)
    SQLModel.metadata.create_all(eng)
    return eng


def get_session():
    with Session(engine) as session:
        yield session
