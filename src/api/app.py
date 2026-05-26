from fastapi import FastAPI

from src.api.routes import health, items, orders, listings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Inventory Operations API",
        description="REST API for multi-platform inventory management",
        version="1.0.0",
    )

    app.include_router(health.router)
    app.include_router(items.router)
    app.include_router(orders.router)
    app.include_router(listings.router)

    return app


app = create_app()
