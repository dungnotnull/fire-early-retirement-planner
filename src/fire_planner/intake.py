"""Financial intake sub-skill -- validates and normalizes user inputs."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .models import AssetAllocation, FinancialProfile, RiskTolerance, TaxStatus
from .utils import (
    configure_logging,
    get_logger,
    normalize_allocation_dict,
    to_float,
    to_int,
    validate_age,
    validate_ratio,
)

configure_logging()
logger = get_logger("fire_planner.intake")


REQUIRED_FIELDS: Tuple[str, ...] = (
    "current_age",
    "retirement_age",
    "life_expectancy",
    "current_portfolio",
    "annual_gross_income",
    "annual_expenses",
    "annual_savings",
    "allocation",
    "risk_tolerance",
)


class FinancialIntake:
    """Capture, validate and normalize a user's financial profile."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FinancialProfile:
        """Build a FinancialProfile from a raw dict, raising on missing/invalid data."""
        missing = [f for f in REQUIRED_FIELDS if f not in data or data[f] is None]
        if missing:
            raise ValueError(
                f"Incomplete intake: missing required fields {missing}. "
                "Please provide these values before analysis."
            )

        current_age = validate_age(data["current_age"], "current_age")
        retirement_age = validate_age(data["retirement_age"], "retirement_age")
        life_expectancy = validate_age(data["life_expectancy"], "life_expectancy")

        if retirement_age < current_age:
            raise ValueError(f"retirement_age ({retirement_age}) must be greater than or equal to current_age ({current_age})")
        if life_expectancy <= retirement_age:
            raise ValueError(
                f"life_expectancy ({life_expectancy}) must be greater than "
                f"retirement_age ({retirement_age})"
            )

        current_portfolio = to_float(data["current_portfolio"], "current_portfolio")
        if current_portfolio < 0:
            raise ValueError("current_portfolio cannot be negative")

        annual_gross_income = to_float(data["annual_gross_income"], "annual_gross_income")
        annual_expenses = to_float(data["annual_expenses"], "annual_expenses")
        annual_savings = to_float(data["annual_savings"], "annual_savings")

        if annual_expenses <= 0:
            raise ValueError("annual_expenses must be positive")
        if annual_savings < 0:
            raise ValueError("annual_savings cannot be negative")
        if annual_savings > annual_gross_income:
            logger.warning(
                "annual_savings (%.2f) exceeds annual_gross_income (%.2f)",
                annual_savings,
                annual_gross_income,
            )

        allocation = cls._parse_allocation(data["allocation"])

        risk_tolerance = cls._parse_risk_tolerance(data["risk_tolerance"])

        optional = cls._parse_optional(data)

        notes = cls._derive_notes(
            current_age, retirement_age, life_expectancy, annual_gross_income,
            annual_expenses, annual_savings, allocation, optional
        )

        profile = FinancialProfile(
            current_age=current_age,
            retirement_age=retirement_age,
            life_expectancy=life_expectancy,
            current_portfolio=current_portfolio,
            annual_gross_income=annual_gross_income,
            annual_expenses=annual_expenses,
            annual_savings=annual_savings,
            allocation=allocation,
            risk_tolerance=risk_tolerance,
            **optional,
            notes=notes,
        )
        logger.info("Intake completed for age %d -> retire %d", current_age, retirement_age)
        return profile

    @staticmethod
    def _parse_allocation(raw: Any) -> AssetAllocation:
        if isinstance(raw, AssetAllocation):
            return raw
        if isinstance(raw, dict):
            normalized = normalize_allocation_dict(raw)
            return AssetAllocation(
                equities=normalized.get("equities", 0.0),
                bonds=normalized.get("bonds", 0.0),
                cash=normalized.get("cash", 0.0),
                alternatives=normalized.get("alternatives", 0.0),
                us_equities=normalized.get("us_equities"),
                international_equities=normalized.get("international_equities"),
                crypto=normalized.get("crypto"),
                real_estate=normalized.get("real_estate"),
            )
        raise TypeError(f"allocation must be a dict or AssetAllocation; got {type(raw).__name__}")

    @staticmethod
    def _parse_risk_tolerance(raw: Any) -> RiskTolerance:
        if isinstance(raw, RiskTolerance):
            return raw
        if isinstance(raw, str):
            try:
                return RiskTolerance(raw.lower())
            except ValueError as exc:
                raise ValueError(
                    f"risk_tolerance must be one of "
                    f"{[rt.value for rt in RiskTolerance]}; got {raw!r}"
                ) from exc
        raise TypeError(
            f"risk_tolerance must be a string or RiskTolerance; got {type(raw).__name__}"
        )

    @staticmethod
    def _parse_optional(data: Dict[str, Any]) -> Dict[str, Any]:
        optional: Dict[str, Any] = {}

        if "target_withdrawal_rate" in data and data["target_withdrawal_rate"] is not None:
            optional["target_withdrawal_rate"] = validate_ratio(
                data["target_withdrawal_rate"], "target_withdrawal_rate"
            )

        if "monthly_expenses" in data and data["monthly_expenses"] is not None:
            optional["monthly_expenses"] = to_float(data["monthly_expenses"], "monthly_expenses")

        if "emergency_fund_months" in data and data["emergency_fund_months"] is not None:
            optional["emergency_fund_months"] = to_float(
                data["emergency_fund_months"], "emergency_fund_months"
            )

        if "desired_legacy" in data and data["desired_legacy"] is not None:
            optional["desired_legacy"] = to_float(data["desired_legacy"], "desired_legacy")

        if "pension_income" in data and data["pension_income"] is not None:
            optional["pension_income"] = to_float(data["pension_income"], "pension_income")

        if "social_security_annual" in data and data["social_security_annual"] is not None:
            optional["social_security_annual"] = to_float(
                data["social_security_annual"], "social_security_annual"
            )

        if "fee_rate" in data and data["fee_rate"] is not None:
            fee = to_float(data["fee_rate"], "fee_rate")
            if fee < 0 or fee > 0.5:
                raise ValueError("fee_rate must be between 0 and 0.5")
            optional["fee_rate"] = fee
        else:
            optional["fee_rate"] = 0.001

        if "inflation_assumption" in data and data["inflation_assumption"] is not None:
            optional["inflation_assumption"] = to_float(
                data["inflation_assumption"], "inflation_assumption"
            )

        if "expected_return_override" in data and data["expected_return_override"] is not None:
            optional["expected_return_override"] = to_float(
                data["expected_return_override"], "expected_return_override"
            )

        if "tax_status" in data and data["tax_status"] is not None:
            optional["tax_status"] = cls._parse_tax_status(data["tax_status"])

        return optional

    @staticmethod
    def _parse_tax_status(raw: Any) -> TaxStatus:
        if isinstance(raw, TaxStatus):
            return raw
        if not isinstance(raw, dict):
            raise TypeError("tax_status must be a dict or TaxStatus")
        ratios = {
            "tax_deferred_ratio": raw.get("tax_deferred_ratio", 0.0),
            "taxable_ratio": raw.get("taxable_ratio", 0.0),
            "tax_free_ratio": raw.get("tax_free_ratio", 0.0),
        }
        for key, val in ratios.items():
            ratios[key] = validate_ratio(val, key)
        total = sum(ratios.values())
        if abs(total - 1.0) > 1e-9 and total != 0.0:
            raise ValueError(f"tax_status ratios must sum to 1.0; got {total}")
        return TaxStatus(
            tax_deferred_ratio=ratios["tax_deferred_ratio"],
            taxable_ratio=ratios["taxable_ratio"],
            tax_free_ratio=ratios["tax_free_ratio"],
            marginal_tax_rate=validate_ratio(raw.get("marginal_tax_rate", 0.0), "marginal_tax_rate"),
            effective_tax_rate=validate_ratio(raw.get("effective_tax_rate", 0.0), "effective_tax_rate"),
        )

    @staticmethod
    def _derive_notes(
        current_age: int,
        retirement_age: int,
        life_expectancy: int,
        annual_gross_income: float,
        annual_expenses: float,
        annual_savings: float,
        allocation: AssetAllocation,
        optional: Dict[str, Any],
    ) -> List[str]:
        notes: List[str] = []
        sr = annual_savings / annual_gross_income if annual_gross_income > 0 else 0.0
        notes.append(
            f"Derived savings rate: {sr:.1%} of gross income."
        )
        if allocation.has_shortfall():
            shortfall = 1.0 - allocation.total()
            notes.append(
                f"Allocation sums to {allocation.total():.1%}; treating {shortfall:.1%} as unspecified."
            )
        if optional.get("emergency_fund_months") is None:
            notes.append(
                "Emergency fund months not provided; assumed present for analysis."
            )
        return notes

    @classmethod
    def infer_monthly_expenses(cls, profile: FinancialProfile) -> FinancialProfile:
        """If monthly_expenses is missing but annual_expenses exists, infer it."""
        if profile.monthly_expenses is not None:
            return profile
        return profile  # dataclass is frozen; caller should reconstruct if needed


    @classmethod
    def ask_clarifying_questions(cls, data: Dict[str, Any]) -> List[str]:
        """Return targeted questions for missing required inputs only."""
        questions: List[str] = []
        for field in REQUIRED_FIELDS:
            if field not in data or data[field] is None:
                questions.append(f"What is your {field.replace('_', ' ')}?")
        return questions

