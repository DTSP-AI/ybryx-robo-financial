"""Robot/Equipment catalog API endpoints."""

from typing import Any, Optional
from fastapi import APIRouter, Query
import structlog

logger = structlog.get_logger()

router = APIRouter()


# Mock robot data (TODO: Replace with database queries)
MOCK_ROBOTS = [
    {
        "id": "r1",
        "name": "Mobile Shelf AMR",
        "manufacturer": "Locus Robotics",
        "category": "AMR",
        "description": "Autonomous mobile robot that brings shelves directly to workers, reducing walk time by 70%",
        "payload": "500 lbs",
        "autonomy_level": "Level 4",
        "lease_from": "$1,299",
        "use_case": "logistics",
        "specifications": {
            "weight": "120 lbs",
            "dimensions": "36\" x 24\" x 48\"",
            "battery_life": "8 hours",
        },
    },
    {
        "id": "r2",
        "name": "Heavy Duty Pallet Bot",
        "manufacturer": "Fetch Robotics",
        "category": "AGV",
        "description": "Industrial-grade pallet mover for high-volume warehouse operations",
        "payload": "3,000 lbs",
        "autonomy_level": "Level 4",
        "lease_from": "$2,499",
        "use_case": "logistics",
    },
    {
        "id": "r3",
        "name": "Agricultural Spray Drone",
        "manufacturer": "DJI Agras",
        "category": "Drone",
        "description": "Cover 40 acres per hour with precision crop spraying and monitoring",
        "payload": "10 gallons",
        "autonomy_level": "Level 3",
        "lease_from": "$899",
        "use_case": "agriculture",
    },
]


@router.get("/robots", response_model=dict[str, Any])
async def list_robots(
    search: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Category filter"),
    use_case: Optional[str] = Query(None, description="Use case filter"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    """List robots with optional filtering.

    Args:
        search: Search query
        category: Category filter
        use_case: Use case filter
        page: Page number
        limit: Results per page

    Returns:
        dict: Paginated robot list
    """
    try:
        logger.info(
            "robots_list_request",
            search=search,
            category=category,
            use_case=use_case,
            page=page,
        )

        # Filter mock data
        robots = MOCK_ROBOTS.copy()

        if search:
            search_lower = search.lower()
            robots = [
                r
                for r in robots
                if search_lower in r["name"].lower()
                or search_lower in r["description"].lower()
                or search_lower in r["manufacturer"].lower()
            ]

        if category:
            robots = [r for r in robots if r["category"].lower() == category.lower()]

        if use_case:
            robots = [r for r in robots if r["use_case"].lower() == use_case.lower()]

        # Pagination
        total = len(robots)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_robots = robots[start_idx:end_idx]

        return {
            "success": True,
            "data": {
                "robots": paginated_robots,
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
            "robots_list_failed",
            error=str(e),
            exc_info=True,
        )
        return {
            "success": False,
            "data": None,
            "error": {
                "message": "Failed to retrieve robots",
                "code": "internal_error",
            },
        }


@router.get("/robots/{robot_id}", response_model=dict[str, Any])
async def get_robot(robot_id: str) -> dict[str, Any]:
    """Get robot details by ID.

    Args:
        robot_id: Robot identifier

    Returns:
        dict: Robot details
    """
    try:
        robot = next((r for r in MOCK_ROBOTS if r["id"] == robot_id), None)

        if not robot:
            return {
                "success": False,
                "data": None,
                "error": {
                    "message": "Robot not found",
                    "code": "not_found",
                },
            }

        # Add related robots
        related_robots = [
            r["id"] for r in MOCK_ROBOTS if r["id"] != robot_id and r["category"] == robot["category"]
        ][:3]

        robot_data = {
            **robot,
            "related_robots": related_robots,
        }

        return {
            "success": True,
            "data": robot_data,
            "error": None,
        }

    except Exception as e:
        logger.error(
            "robot_get_failed",
            robot_id=robot_id,
            error=str(e),
            exc_info=True,
        )
        return {
            "success": False,
            "data": None,
            "error": {
                "message": "Failed to retrieve robot",
                "code": "internal_error",
            },
        }
