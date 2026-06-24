"""Utility helpers for validation, statistics, logging and reporting."""
from __future__ import annotations

import logging
import math
import re
from typing import Any, Dict, List, Optional


def configure_logging(level: int = logging.INFO) -> None:
    """Configure a consistent logger for the package."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp a numeric value to [low, high]."""
    return max(low, min(high, value))


def percentile(data: List[float], pct: float) -> float:
    """Return the percentile of a numeric list using nearest-rank method."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    if pct <= 0:
        return sorted_data[0]
    if pct >= 100:
        return sorted_data[-1]
    k = (len(sorted_data) - 1) * pct / 100.0
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    d0 = sorted_data[f] * (c - k)
    d1 = sorted_data[c] * (k - f)
    return d0 + d1


def to_float(value: Any, field_name: str = "value") -> float:
    """Coerce a value to float with a clear error."""
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric; got {value!r}") from exc


def to_int(value: Any, field_name: str = "value") -> int:
    """Coerce a value to int with a clear error."""
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer; got {value!r}") from exc


def non_empty(value: Any, field_name: str = "value") -> str:
    """Validate a non-empty string."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string; got {value!r}")
    return value.strip()


def validate_age(value: int, field_name: str = "age", min_age: int = 18, max_age: int = 120) -> int:
    """Validate an age value."""
    value = to_int(value, field_name)
    if value < min_age or value > max_age:
        raise ValueError(f"{field_name} must be between {min_age} and {max_age}; got {value}")
    return value


def validate_ratio(value: float, field_name: str = "ratio") -> float:
    """Validate a fractional ratio [0, 1]."""
    value = to_float(value, field_name)
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{field_name} must be between 0 and 1; got {value}")
    return value


def interpolate_glide_equity(age: int, glide_path: Dict[int, float]) -> float:
    """Linear-interpolate equity target from a glide-path table."""
    ages = sorted(glide_path.keys())
    if age <= ages[0]:
        return glide_path[ages[0]]
    if age >= ages[-1]:
        return glide_path[ages[-1]]
    lower = max(a for a in ages if a <= age)
    upper = min(a for a in ages if a >= age)
    if lower == upper:
        return glide_path[lower]
    frac = (age - lower) / (upper - lower)
    return glide_path[lower] + frac * (glide_path[upper] - glide_path[lower])


def humanize_dollars(amount: float) -> str:
    """Pretty-print a dollar amount with thousands separators."""
    return f"${amount:,.2f}"


def normalize_allocation_dict(raw: Dict[str, Any]) -> Dict[str, float]:
    """Normalize a raw allocation dict, treating missing keys as 0 and validating sum."""
    allowed = {
        "equities",
        "bonds",
        "cash",
        "alternatives",
        "us_equities",
        "international_equities",
        "crypto",
        "real_estate",
    }
    out: Dict[str, float] = {}
    total = 0.0
    for key in allowed:
        val = raw.get(key, 0.0)
        f = to_float(val, key)
        if f < 0:
            raise ValueError(f"Allocation component {key} cannot be negative")
        out[key] = f
        if key in {"equities", "bonds", "cash", "alternatives"}:
            total += f
    if total > 1.0 + 1e-9:
        raise ValueError(f"Core allocation fractions sum to {total}; cannot exceed 1.0")
    return out


def slugify(text: str) -> str:
    """Create a URL-friendly slug."""
    return re.sub(r"[^a-z0-9-]+", "-", text.lower()).strip("-")


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Divide with a safe default for zero denominator."""
    if denominator == 0:
        return default
    return numerator / denominator


def format_percent(value: float, decimals: int = 1) -> str:
    """Format a fraction as a percentage string."""
    return f"{value * 100:.{decimals}f}%"
