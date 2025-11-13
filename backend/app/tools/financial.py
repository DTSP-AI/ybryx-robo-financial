"""Financial scoring and risk assessment tools."""

from typing import Any, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import structlog

logger = structlog.get_logger()


class FinancialScoringInput(BaseModel):
    """Input schema for financial scoring."""

    annual_revenue: str = Field(description="Annual revenue range")
    business_age: str = Field(description="Business age range")
    credit_rating: str = Field(description="Estimated credit rating")
    industry: str = Field(description="Industry sector")


class FinancialScoringTool(BaseTool):
    """Tool to calculate financial scores and lease eligibility."""

    name: str = "financial_scoring"
    description: str = (
        "Calculate financial score and lease eligibility based on business financials. "
        "Returns risk score (0-100), recommended lease terms, and approval probability."
    )
    args_schema: Type[BaseModel] = FinancialScoringInput

    def _run(
        self,
        annual_revenue: str,
        business_age: str,
        credit_rating: str,
        industry: str,
    ) -> dict[str, Any]:
        """Execute financial scoring logic.

        Args:
            annual_revenue: Revenue range
            business_age: Business age range
            credit_rating: Credit rating estimate
            industry: Industry sector

        Returns:
            dict: Financial score analysis
        """
        # Revenue score
        revenue_scores = {
            "0-500k": 20,
            "500k-1m": 40,
            "1m-5m": 70,
            "5m-10m": 85,
            "10m+": 95,
        }
        revenue_score = revenue_scores.get(annual_revenue, 50)

        # Business age score
        age_scores = {
            "0-1": 30,
            "1-2": 50,
            "2-5": 75,
            "5+": 90,
        }
        age_score = age_scores.get(business_age, 50)

        # Credit rating score
        credit_scores = {
            "excellent": 95,
            "good": 80,
            "fair": 60,
            "poor": 30,
        }
        credit_score = credit_scores.get(credit_rating, 50)

        # Industry risk modifier
        industry_modifiers = {
            "logistics": 1.0,
            "manufacturing": 1.0,
            "agriculture": 0.9,
            "delivery": 0.95,
            "construction": 0.85,
            "retail": 0.95,
        }
        industry_modifier = industry_modifiers.get(industry, 1.0)

        # Calculate composite score
        base_score = (revenue_score * 0.4 + age_score * 0.3 + credit_score * 0.3)
        final_score = int(base_score * industry_modifier)

        # Determine approval status
        if final_score >= 70:
            status = "approved"
            approval_probability = "high"
            max_lease_value = 500000
        elif final_score >= 50:
            status = "needs_review"
            approval_probability = "medium"
            max_lease_value = 250000
        else:
            status = "declined"
            approval_probability = "low"
            max_lease_value = 50000

        # Recommended terms
        if final_score >= 70:
            lease_terms = [24, 36, 48]
            interest_rate_range = "5-7%"
        elif final_score >= 50:
            lease_terms = [24, 36]
            interest_rate_range = "8-12%"
        else:
            lease_terms = [12, 24]
            interest_rate_range = "13-18%"

        result = {
            "financial_score": final_score,
            "status": status,
            "approval_probability": approval_probability,
            "max_lease_value": max_lease_value,
            "recommended_terms": {
                "lease_terms_months": lease_terms,
                "interest_rate_range": interest_rate_range,
            },
            "breakdown": {
                "revenue_score": revenue_score,
                "age_score": age_score,
                "credit_score": credit_score,
                "industry_modifier": industry_modifier,
            },
        }

        logger.info(
            "financial_scoring_completed",
            score=final_score,
            status=status,
        )

        return result


class RiskRulesInput(BaseModel):
    """Input schema for risk rules validation."""

    financial_score: int = Field(description="Financial score from scoring tool")
    equipment_value: float = Field(description="Total equipment value")
    industry: str = Field(description="Industry sector")


class RiskRulesTool(BaseTool):
    """Tool to apply compliance and risk rules."""

    name: str = "risk_rules_validator"
    description: str = (
        "Apply compliance and risk validation rules to lease applications. "
        "Returns compliance status and any required actions."
    )
    args_schema: Type[BaseModel] = RiskRulesInput

    def _run(
        self,
        financial_score: int,
        equipment_value: float,
        industry: str,
    ) -> dict[str, Any]:
        """Execute risk rules validation.

        Args:
            financial_score: Financial score
            equipment_value: Equipment value
            industry: Industry sector

        Returns:
            dict: Compliance validation results
        """
        issues = []
        warnings = []
        required_actions = []

        # Rule 1: Minimum financial score
        if financial_score < 40:
            issues.append("Financial score below minimum threshold (40)")
            required_actions.append("Manual underwriting review required")

        # Rule 2: High value equipment
        if equipment_value > 300000:
            warnings.append("High value equipment requires additional documentation")
            required_actions.append("Submit audited financial statements")

        # Rule 3: High-risk industries
        high_risk_industries = ["construction"]
        if industry in high_risk_industries:
            warnings.append(f"Industry '{industry}' requires enhanced due diligence")
            required_actions.append("Provide industry-specific references")

        # Rule 4: Value-to-score ratio
        max_safe_value = financial_score * 5000
        if equipment_value > max_safe_value:
            issues.append(f"Equipment value exceeds recommended limit for financial score")
            required_actions.append("Consider reducing equipment value or co-signer")

        # Determine compliance status
        if issues:
            compliance_status = "failed"
        elif warnings:
            compliance_status = "conditional"
        else:
            compliance_status = "passed"

        result = {
            "compliance_status": compliance_status,
            "issues": issues,
            "warnings": warnings,
            "required_actions": required_actions,
            "rules_checked": [
                "minimum_financial_score",
                "high_value_equipment",
                "industry_risk",
                "value_to_score_ratio",
            ],
        }

        logger.info(
            "risk_rules_validated",
            status=compliance_status,
            issues_count=len(issues),
        )

        return result
