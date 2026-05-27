"""Tests for PhysicalItem model."""
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from src.models.item import PhysicalItem, MAX_SCRAPING_ATTEMPTS


def _make_item(**kw):
    defaults = dict(lpn="LPN001", asin="B08XYZ", purchase_price=Decimal("50.00"),
                    purchase_date=date.today())
    defaults.update(kw)
    return PhysicalItem(**defaults)


def test_validate_ok():
    item = _make_item()
    assert item.validate() == []


def test_validate_negative_price():
    item = _make_item(purchase_price=Decimal("-1"))
    errors = item.validate()
    assert any("purchase_price" in e for e in errors)


def test_validate_negative_weight():
    item = _make_item(weight_kg=Decimal("-0.5"))
    errors = item.validate()
    assert any("weight_kg" in e for e in errors)


def test_validate_future_date():
    item = _make_item(purchase_date=date.today() + timedelta(days=1))
    errors = item.validate()
    assert any("future" in e for e in errors)


def test_scraping_not_paused():
    item = _make_item(scraping_attempts=0)
    assert not item.scraping_paused


def test_scraping_paused_at_max():
    item = _make_item(scraping_attempts=MAX_SCRAPING_ATTEMPTS)
    assert item.scraping_paused


def test_increment_scraping():
    item = _make_item(scraping_attempts=0)
    item.increment_scraping()
    assert item.scraping_attempts == 1
    assert item.last_scraped_at is not None
    assert not item.scraping_needs_manual


def test_increment_scraping_triggers_manual():
    item = _make_item(scraping_attempts=MAX_SCRAPING_ATTEMPTS - 1)
    item.increment_scraping()
    assert item.scraping_paused
    assert item.scraping_needs_manual


def test_reset_scraping():
    item = _make_item(scraping_attempts=5, scraping_needs_manual=True)
    item.reset_scraping(Decimal("99.99"))
    assert item.scraped_price == Decimal("99.99")
    assert item.scraping_attempts == 0
    assert not item.scraping_needs_manual


def test_image_url_list_empty():
    item = _make_item(image_urls=None)
    assert item.image_url_list() == []


def test_image_url_list_single():
    item = _make_item(image_urls="https://img.com/1.jpg")
    assert item.image_url_list() == ["https://img.com/1.jpg"]


def test_image_url_list_multiple():
    item = _make_item(image_urls="https://a.com/1.jpg, https://b.com/2.jpg")
    assert len(item.image_url_list()) == 2


def test_image_url_list_trims():
    item = _make_item(image_urls=" https://a.com/1.jpg , , https://b.com/2.jpg ")
    urls = item.image_url_list()
    assert len(urls) == 2
    assert urls[0] == "https://a.com/1.jpg"


def test_available_default():
    item = _make_item()
    assert item.available is True


def test_do_not_list_default():
    item = _make_item()
    assert item.do_not_list is False
