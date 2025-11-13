"""Dealer lookup and matching tools."""

from typing import Any, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import asyncio

from app.database.models import Dealer

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
        # Use asyncio to run the async database query
        return asyncio.run(self._async_run(zip_code, specialty, max_results))

    async def _async_run(
        self,
        zip_code: str,
        specialty: str = "",
        max_results: int = 5,
    ) -> dict[str, Any]:
        """Execute dealer lookup (async implementation).

        Args:
            zip_code: ZIP code to search near
            specialty: Optional specialty filter
            max_results: Maximum dealers to return

        Returns:
            dict: Matching dealers
        """
        from app.database.session import async_session_maker

        async with async_session_maker() as session:
            try:
                # Build query for active dealers
                query = select(Dealer).where(Dealer.is_active == True)

                # Execute query
                result = await session.execute(query)
                all_dealers = result.scalars().all()

                # Filter by ZIP code (check if zip_code is in dealer's zip_codes array)
                zip_prefix = zip_code[:3]
                filtered_dealers = []

                for dealer in all_dealers:
                    # Check if any of the dealer's zip codes match the prefix
                    zip_codes = dealer.zip_codes if dealer.zip_codes else []
                    if any(str(zc).startswith(zip_prefix) for zc in zip_codes):
                        # Filter by specialty if provided
                        if specialty:
                            specialties = dealer.specialties if dealer.specialties else []
                            if not any(specialty.lower() in str(s).lower() for s in specialties):
                                continue

                        filtered_dealers.append({
                            "id": str(dealer.id),
                            "name": dealer.name,
                            "coverage": dealer.coverage,
                            "address": dealer.address,
                            "phone": dealer.phone,
                            "email": dealer.email,
                            "website": dealer.website,
                            "zip_codes": dealer.zip_codes,
                            "specialties": dealer.specialties,
                        })

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

            except Exception as e:
                logger.error(
                    "dealer_lookup_error",
                    error=str(e),
                    zip_code=zip_code,
                )
                return {
                    "dealers": [],
                    "total_found": 0,
                    "search_zip": zip_code,
                    "error": str(e),
                }
