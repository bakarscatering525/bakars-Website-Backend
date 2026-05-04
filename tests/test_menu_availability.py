import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.api.v1.admin import (  # noqa: E402
    normalize_availability_scope,
    resolve_availability_flags,
    determine_scope_from_flags,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("daily", "daily"),
        ("Daily", "daily"),
        ("daily_menu", "daily"),
        ("meal_plan", "meal_plan"),
        ("weekly", "meal_plan"),
        ("both", "both"),
        ("Daily Menu", "daily"),
        ("meal plan", "meal_plan"),
        ("Daily-and-meal_plan", "both"),
    ],
)
def test_normalize_availability_scope_aliases(raw, expected):
    assert normalize_availability_scope(raw) == expected


def test_normalize_availability_scope_rejects_invalid():
    with pytest.raises(HTTPException) as exc_info:
        normalize_availability_scope("weekly_only_invalid")
    assert exc_info.value.status_code == 400
    assert "availability_scope" in exc_info.value.detail


@pytest.mark.parametrize(
    "scope,expected",
    [
        (("daily", None, None, None), ("daily", True, False)),
        (("meal_plan", None, None, None), ("meal_plan", False, True)),
        (("both", None, None, None), ("both", True, True)),
        ((None, "daily_menu", None, None), ("daily", True, False)),
    ],
)
def test_resolve_availability_flags_prefers_scope(scope, expected):
    resolved = resolve_availability_flags(*scope)
    assert resolved == expected


def test_resolve_availability_flags_uses_boolean_fallbacks():
    scope_label, is_daily, is_meal_plan = resolve_availability_flags(
        None, None, True, True
    )
    assert scope_label == "both"
    assert is_daily and is_meal_plan

    scope_label, is_daily, is_meal_plan = resolve_availability_flags(
        None, None, True, False
    )
    assert scope_label == "daily"
    assert is_daily and not is_meal_plan


def test_resolve_availability_flags_rejects_missing_selection():
    with pytest.raises(HTTPException) as exc_info:
        resolve_availability_flags(None, None, False, False)
    assert exc_info.value.status_code == 400


@pytest.mark.parametrize(
    "daily,meal_plan,expected",
    [
        (True, False, "daily"),
        (False, True, "meal_plan"),
        (True, True, "both"),
    ],
)
def test_determine_scope_from_flags(daily, meal_plan, expected):
    assert determine_scope_from_flags(daily, meal_plan) == expected
