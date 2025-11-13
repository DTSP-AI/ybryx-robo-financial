"""Robot catalog search tools."""

from typing import Any, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import asyncio

from app.database.models import Robot, Industry

logger = structlog.get_logger()


class RobotSearchInput(BaseModel):
    """Input schema for robot catalog search."""

    query: str = Field(description="Search query for robot name or description")
    category: str = Field(default="", description="Equipment category filter (AMR, AGV, Drone, etc)")
    use_case: str = Field(default="", description="Industry/use case filter")
    max_results: int = Field(default=5, description="Maximum robots to return")


class RobotCatalogTool(BaseTool):
    """Tool to search robot equipment catalog."""

    name: str = "robot_catalog_search"
    description: str = (
        "Search the robot equipment catalog by name, category, or use case. "
        "Returns matching robots with specifications and lease pricing."
    )
    args_schema: Type[BaseModel] = RobotSearchInput

    def _run(
        self,
        query: str,
        category: str = "",
        use_case: str = "",
        max_results: int = 5,
    ) -> dict[str, Any]:
        """Execute robot catalog search.

        Args:
            query: Search query
            category: Category filter
            use_case: Use case filter
            max_results: Max results

        Returns:
            dict: Matching robots
        """
        # Use asyncio to run the async database query
        return asyncio.run(self._async_run(query, category, use_case, max_results))

    async def _async_run(
        self,
        query: str,
        category: str = "",
        use_case: str = "",
        max_results: int = 5,
    ) -> dict[str, Any]:
        """Execute robot catalog search (async implementation).

        Args:
            query: Search query
            category: Category filter
            use_case: Use case filter
            max_results: Max results

        Returns:
            dict: Matching robots
        """
        from app.database.session import async_session_maker

        async with async_session_maker() as session:
            try:
                # Build query for active robots
                db_query = select(Robot).where(Robot.is_active == True)

                # Add text search filters (name, description, manufacturer)
                if query:
                    query_lower = query.lower()
                    db_query = db_query.where(
                        or_(
                            Robot.name.ilike(f"%{query_lower}%"),
                            Robot.description.ilike(f"%{query_lower}%"),
                            Robot.manufacturer.ilike(f"%{query_lower}%"),
                        )
                    )

                # Filter by category
                if category:
                    db_query = db_query.where(Robot.category.ilike(f"%{category}%"))

                # Filter by use_case (Industry enum)
                if use_case:
                    try:
                        # Try to match as enum value
                        use_case_enum = Industry[use_case.upper()]
                        db_query = db_query.where(Robot.use_case == use_case_enum)
                    except KeyError:
                        # If not exact match, try partial match
                        db_query = db_query.where(
                            Robot.use_case.cast(str).ilike(f"%{use_case}%")
                        )

                # Limit results
                db_query = db_query.limit(max_results)

                # Execute query
                result = await session.execute(db_query)
                robots = result.scalars().all()

                # Format results
                formatted_robots = []
                for robot in robots:
                    formatted_robots.append({
                        "id": str(robot.id),
                        "name": robot.name,
                        "manufacturer": robot.manufacturer,
                        "category": robot.category,
                        "description": robot.description,
                        "use_case": robot.use_case.value if robot.use_case else None,
                        "payload": robot.payload,
                        "autonomy_level": robot.autonomy_level,
                        "lease_from": robot.lease_from,
                        "lease_price_monthly": robot.lease_price_monthly,
                        "specifications": robot.specifications,
                        "image_url": robot.image_url,
                    })

                logger.info(
                    "robot_search_completed",
                    query=query,
                    category=category,
                    use_case=use_case,
                    results_count=len(formatted_robots),
                )

                return {
                    "robots": formatted_robots,
                    "total_found": len(formatted_robots),
                    "search_params": {
                        "query": query,
                        "category": category,
                        "use_case": use_case,
                    },
                }

            except Exception as e:
                logger.error(
                    "robot_search_error",
                    error=str(e),
                    query=query,
                )
                return {
                    "robots": [],
                    "total_found": 0,
                    "search_params": {
                        "query": query,
                        "category": category,
                        "use_case": use_case,
                    },
                    "error": str(e),
                }
