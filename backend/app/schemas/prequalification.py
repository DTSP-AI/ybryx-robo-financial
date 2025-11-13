"""Prequalification schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class PrequalificationCreate(BaseModel):
    """Schema for creating a prequalification application."""

    business_name: str = Field(..., min_length=1, max_length=255)
    business_type: str = Field(..., pattern="^(llc|corporation|partnership|sole-proprietor)$")
    industry: str = Field(
        ...,
        pattern="^(logistics|agriculture|manufacturing|delivery|construction|retail)$",
    )
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=50)
    selected_equipment: list[str] = Field(..., min_items=1)
    quantity: str = Field(..., pattern="^(1|2-5|6-10|11-20|20\\+)$")
    annual_revenue: str = Field(..., pattern="^(0-500k|500k-1m|1m-5m|5m-10m|10m\\+)$")
    business_age: str = Field(..., pattern="^(0-1|1-2|2-5|5\\+)$")
    credit_rating: str = Field(..., pattern="^(excellent|good|fair|poor)$")
    consent: bool = Field(..., description="Must be True")


class PreliminaryTerms(BaseModel):
    """Preliminary lease terms."""

    estimated_monthly_payment: Optional[float] = None
    lease_term_months: Optional[int] = None
    total_equipment_value: Optional[float] = None


class PrequalificationResponse(BaseModel):
    """Response after prequalification submission."""

    application_id: str
    status: str
    estimated_decision_date: Optional[datetime] = None
    preliminary_terms: Optional[PreliminaryTerms] = None


class PrequalificationDetail(BaseModel):
    """Detailed prequalification information."""

    id: str
    application_number: str
    business_name: str
    business_type: str
    industry: str
    email: str
    phone: str
    selected_equipment: list[str]
    quantity: str
    annual_revenue: str
    business_age: str
    credit_rating: str
    status: str
    agent_analysis: Optional[dict] = None
    preliminary_terms: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
