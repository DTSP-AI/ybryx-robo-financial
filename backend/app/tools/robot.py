"""Robot catalog search tools."""

from typing import Any, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import structlog

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
        # TODO: Replace with actual database query
        # For now, return mock data

        mock_robots = [
            {
                "id": "r1",
                "name": "Mobile Shelf AMR",
                "manufacturer": "Locus Robotics",
                "category": "AMR",
                "description": "Autonomous mobile robot for warehouse order picking",
                "use_case": "logistics",
                "payload": "500 lbs",
                "lease_from": "$1,299/month",
                "specifications": {
                    "autonomy_level": "Level 4",
                    "battery_life": "8 hours",
                    "charging_time": "1 hour",
                },
            },
            {
                "id": "r2",
                "name": "Heavy Duty Pallet Bot",
                "manufacturer": "Fetch Robotics",
                "category": "AGV",
                "description": "Industrial pallet mover for heavy loads",
                "use_case": "logistics",
                "payload": "3,000 lbs",
                "lease_from": "$2,499/month",
                "specifications": {
                    "autonomy_level": "Level 4",
                    "battery_life": "10 hours",
                    "max_speed": "3 mph",
                },
            },
            {
                "id": "r3",
                "name": "Agricultural Spray Drone",
                "manufacturer": "DJI Agras",
                "category": "Drone",
                "description": "Precision crop spraying drone",
                "use_case": "agriculture",
                "payload": "10 gallons",
                "lease_from": "$899/month",
                "specifications": {
                    "autonomy_level": "Level 3",
                    "flight_time": "20 minutes",
                    "coverage_rate": "40 acres/hour",
                },
            },
        ]

        # Filter by query
        query_lower = query.lower()
        filtered = [
            r for r in mock_robots
            if query_lower in r["name"].lower()
            or query_lower in r["description"].lower()
            or query_lower in r["manufacturer"].lower()
        ]

        # Filter by category
        if category:
            filtered = [
                r for r in filtered
                if r["category"].lower() == category.lower()
            ]

        # Filter by use case
        if use_case:
            filtered = [
                r for r in filtered
                if r["use_case"].lower() == use_case.lower()
            ]

        # Limit results
        filtered = filtered[:max_results]

        logger.info(
            "robot_search_completed",
            query=query,
            category=category,
            use_case=use_case,
            results_count=len(filtered),
        )

        return {
            "robots": filtered,
            "total_found": len(filtered),
            "search_params": {
                "query": query,
                "category": category,
                "use_case": use_case,
            },
        }
