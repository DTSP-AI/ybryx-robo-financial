"""Prequalification API endpoints."""

from typing import Any
from uuid import uuid4
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.config import settings
from app.deps import get_db
from app.database.models import Prequalification, BusinessType, Industry, PrequalificationStatus
from app.schemas.prequalification import (
    PrequalificationCreate,
    PrequalificationResponse,
    PrequalificationDetail,
    PreliminaryTerms,
)
from app.graph.supervisor import create_supervisor_graph
from app.graph.state import AgentState

logger = structlog.get_logger()

router = APIRouter()


@router.post("/prequalifications", response_model=dict[str, Any])
async def create_prequalification(
    data: PrequalificationCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Submit a prequalification application.

    Args:
        data: Application data
        db: Database session

    Returns:
        dict: Standard API response with application status
    """
    try:
        logger.info(
            "prequalification_submission",
            business_name=data.business_name,
            industry=data.industry,
        )

        # Generate application number
        app_number = f"YB-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid4())[:8].upper()}"

        # Create database record
        prequalification = Prequalification(
            id=uuid4(),
            application_number=app_number,
            business_name=data.business_name,
            business_type=BusinessType(data.business_type),
            industry=Industry(data.industry),
            email=data.email,
            phone=data.phone,
            selected_equipment=data.selected_equipment,
            quantity=data.quantity,
            annual_revenue=data.annual_revenue,
            business_age=data.business_age,
            credit_rating=data.credit_rating,
            consent=data.consent,
            status=PrequalificationStatus.PENDING,
            estimated_decision_date=datetime.utcnow() + timedelta(days=2),
        )

        db.add(prequalification)
        await db.flush()

        # TODO: Invoke financing agent for analysis
        # For now, return pending status
        # graph = create_supervisor_graph()
        # initial_state = {...}
        # result = await graph.ainvoke(initial_state)

        # Mock preliminary analysis
        preliminary_terms = PreliminaryTerms(
            estimated_monthly_payment=1500.00,
            lease_term_months=36,
            total_equipment_value=50000.00,
        )

        response_data = PrequalificationResponse(
            application_id=str(prequalification.id),
            status="pending",
            estimated_decision_date=prequalification.estimated_decision_date,
            preliminary_terms=preliminary_terms,
        )

        await db.commit()

        logger.info(
            "prequalification_created",
            application_id=str(prequalification.id),
            application_number=app_number,
        )

        return {
            "success": True,
            "data": response_data.model_dump(),
            "error": None,
        }

    except Exception as e:
        await db.rollback()
        logger.error(
            "prequalification_creation_failed",
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process prequalification application",
        )


@router.get("/prequalifications/{application_id}", response_model=dict[str, Any])
async def get_prequalification(
    application_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get prequalification application details.

    Args:
        application_id: Application UUID
        db: Database session

    Returns:
        dict: Application details
    """
    try:
        # Query database
        stmt = select(Prequalification).where(Prequalification.id == application_id)
        result = await db.execute(stmt)
        prequalification = result.scalar_one_or_none()

        if not prequalification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prequalification application not found",
            )

        # Convert to response schema
        detail = PrequalificationDetail(
            id=str(prequalification.id),
            application_number=prequalification.application_number,
            business_name=prequalification.business_name,
            business_type=prequalification.business_type.value,
            industry=prequalification.industry.value,
            email=prequalification.email,
            phone=prequalification.phone,
            selected_equipment=prequalification.selected_equipment,
            quantity=prequalification.quantity,
            annual_revenue=prequalification.annual_revenue,
            business_age=prequalification.business_age,
            credit_rating=prequalification.credit_rating,
            status=prequalification.status.value,
            agent_analysis=prequalification.agent_analysis,
            preliminary_terms=prequalification.preliminary_terms,
            created_at=prequalification.created_at,
            updated_at=prequalification.updated_at,
        )

        return {
            "success": True,
            "data": detail.model_dump(),
            "error": None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "prequalification_retrieval_failed",
            application_id=application_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prequalification application",
        )
