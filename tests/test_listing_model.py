"""Tests for Listing model."""
import pytest
from src.models.listing import Listing, PRICE_MODE_STANDARD, PRICE_MODE_MANUAL


def _listing(**kw):
    defaults = dict(id=1, account_id=1, product_id="abc123")
    defaults.update(kw)
    return Listing(**defaults)


def test_status_published():
    assert _listing().status == "published"


def test_status_sold():
    assert _listing(is_sold=True).status == "sold"


def test_status_banned():
    assert _listing(is_banned=True).status == "banned"


def test_status_reserved():
    assert _listing(is_reserved=True).status == "reserved"


def test_status_expired():
    assert _listing(is_expired=True).status == "expired"


def test_status_on_hold():
    assert _listing(is_on_hold=True).status == "on_hold"


def test_status_pending():
    assert _listing(is_pending=True).status == "pending"


def test_status_priority_sold_over_banned():
    assert _listing(is_sold=True, is_banned=True).status == "sold"


def test_total_conversations():
    lst = _listing(conversations_count=5, conversations_accumulated=10)
    assert lst.total_conversations == 15


def test_total_favorites():
    lst = _listing(favorites_count=3, favorites_accumulated=7)
    assert lst.total_favorites == 10


def test_total_views():
    lst = _listing(views_count=100, views_accumulated=200)
    assert lst.total_views == 300


def test_rotate_product_id():
    lst = _listing(
        product_id="old",
        conversations_count=5, favorites_count=3, views_count=100,
    )
    lst.rotate_product_id("new")
    assert lst.product_id == "new"
    assert lst.previous_product_id == "old"
    assert lst.conversations_count == 0
    assert lst.conversations_accumulated == 5
    assert lst.favorites_count == 0
    assert lst.favorites_accumulated == 3
    assert lst.views_count == 0
    assert lst.views_accumulated == 100


def test_rotate_same_id_noop():
    lst = _listing(product_id="same", conversations_count=5)
    lst.rotate_product_id("same")
    assert lst.conversations_count == 5
    assert lst.previous_product_id is None


def test_is_oscillating_false():
    lst = _listing(product_id="abc", previous_product_id=None)
    assert not lst.is_oscillating


def test_is_oscillating_true():
    lst = _listing(product_id="abc", previous_product_id="def")
    assert lst.is_oscillating


def test_default_price_mode():
    lst = _listing()
    assert lst.price_mode == PRICE_MODE_STANDARD
