"""Dealer lookup and matching tools."""

from typing import Any, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import structlog

logger = structlog.get_logger()


class DealerLookupInput(BaseModel):
    """Input schema for dealer lookup."""

    zip_code: str = Field(description="ZIP code for dealer search")
    specialty: str = Field(default="", description="Required dealer specialty")
    max_results: int = Field(default=5, description="Maximum number of dealers to return")


class DealerLookupTool(BaseTool):
    """Tool to find authorized dealers by location and specialty."""

    name: str = "dealer_lookup"
    description: str = (
        "Find authorized dealers near a ZIP code with specific specialties. "
        "Returns dealer information including contact details and coverage areas."
    )
    args_schema: Type[BaseModel] = DealerLookupInput

    def _run(
        self,
        zip_code: str,
        specialty: str = "",
        max_results: int = 5,
    ) -> dict[str, Any]:
        """Execute dealer lookup.

        Args:
            zip_code: ZIP code to search near
            specialty: Optional specialty filter
            max_results: Maximum dealers to return

        Returns:
            dict: Matching dealers
        """
        # TODO: Replace with actual database query
        # For now, return mock data

        mock_dealers = [
            {
                "id": "d1",
                "name": "RoboTech Solutions",
                "zip_codes": ["94105", "94102", "94103"],
                "specialties": ["AMRs", "AGVs", "Warehouse Automation"],
                "phone": "(415) 555-0123",
                "email": "sales@robotechsolutions.com",
                "distance_miles": 2.5,
            },
            {
                "id": "d2",
                "name": "Industrial Automation Partners",
                "zip_codes": ["94104", "94105", "94108"],
                "specialties": ["Robotic Arms", "Manufacturing", "Assembly Lines"],
                "phone": "(415) 555-0456",
                "email": "contact@indautopartners.com",
                "distance_miles": 3.2,
            },
        ]

        # Simple filtering based on ZIP prefix
        zip_prefix = zip_code[:3]
        filtered_dealers = [
            d for d in mock_dealers
            if any(zc.startswith(zip_prefix) for zc in d["zip_codes"])
        ]

        # Filter by specialty if provided
        if specialty:
            filtered_dealers = [
                d for d in filtered_dealers
                if any(specialty.lower() in s.lower() for s in d["specialties"])
            ]

        # Limit results
        filtered_dealers = filtered_dealers[:max_results]

        logger.info(
            "dealer_lookup_completed",
            zip_code=zip_code,
            specialty=specialty,
            results_count=len(filtered_dealers),
        )

        return {
            "dealers": filtered_dealers,
            "total_found": len(filtered_dealers),
            "search_zip": zip_code,
        }
