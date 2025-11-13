"""Dealer API endpoints."""

from typing import Any, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

router = APIRouter()


# Mock dealer data
MOCK_DEALERS = [
    {
        "id": "d1",
        "name": "RoboTech Solutions",
        "coverage": "California, Nevada, Arizona",
        "address": "1234 Innovation Dr, San Francisco, CA 94105",
        "phone": "(415) 555-0123",
        "email": "sales@robotechsolutions.com",
        "specialties": ["AMRs", "AGVs", "Warehouse Automation"],
        "zip_codes": ["94105", "94102", "89101", "85001"],
    },
    {
        "id": "d2",
        "name": "AgriBot Distributors",
        "coverage": "Midwest States",
        "address": "5678 Harvest Ln, Des Moines, IA 50309",
        "phone": "(515) 555-0456",
        "email": "info@agribotdist.com",
        "specialties": ["Agricultural Drones", "Crop Monitoring", "Precision Spraying"],
        "zip_codes": ["50309", "68101", "64101", "55401"],
    },
]


class DealerMatchRequest(BaseModel):
    """Request body for dealer matching."""

    zip_code: str
    equipment_type: str
    industry: str
    contact_info: dict[str, str]


@router.get("/dealers", response_model=dict[str, Any])
async def list_dealers(
    zip_code: Optional[str] = Query(None, description="Filter by ZIP code"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    """List dealers with optional filtering.

    Args:
        zip_code: ZIP code filter
        specialty: Specialty filter
        page: Page number
        limit: Results per page

    Returns:
        dict: Paginated dealer list
    """
    try:
        logger.info(
            "dealers_list_request",
            zip_code=zip_code,
            specialty=specialty,
            page=page,
        )

        dealers = MOCK_DEALERS.copy()

        # Filter by ZIP code
        if zip_code:
            zip_prefix = zip_code[:3]
            dealers = [
                d
                for d in dealers
                if any(zc.startswith(zip_prefix) for zc in d["zip_codes"])
            ]

        # Filter by specialty
        if specialty:
            dealers = [
                d
                for d in dealers
                if any(specialty.lower() in s.lower() for s in d["specialties"])
            ]

        # Pagination
        total = len(dealers)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_dealers = dealers[start_idx:end_idx]

        return {
            "success": True,
            "data": {
                "dealers": paginated_dealers,
                "pagination": {
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "total_pages": (total + limit - 1) // limit,
                },
            },
            "error": None,
        }

    except Exception as e:
        logger.error(
            "dealers_list_failed",
            error=str(e),
            exc_info=True,
        )
        return {
            "success": False,
            "data": None,
            "error": {
                "message": "Failed to retrieve dealers",
                "code": "internal_error",
            },
        }


@router.post("/dealers/match", response_model=dict[str, Any])
async def match_dealers(request: DealerMatchRequest) -> dict[str, Any]:
    """Match dealers based on requirements.

    Args:
        request: Match request data

    Returns:
        dict: Matched dealers
    """
    try:
        logger.info(
            "dealer_match_request",
            zip_code=request.zip_code,
            equipment_type=request.equipment_type,
        )

        # Simple matching logic
        zip_prefix = request.zip_code[:3]
        matched = [
            {
                **d,
                "match_score": 85,  # Mock score
                "estimated_response_time": "1-2 business days",
            }
            for d in MOCK_DEALERS
            if any(zc.startswith(zip_prefix) for zc in d["zip_codes"])
        ]

        return {
            "success": True,
            "data": {
                "matched_dealers": matched,
                "notification_sent": True,
            },
            "error": None,
        }

    except Exception as e:
        logger.error(
            "dealer_match_failed",
            error=str(e),
            exc_info=True,
        )
        return {
            "success": False,
            "data": None,
            "error": {
                "message": "Failed to match dealers",
                "code": "internal_error",
            },
        }
