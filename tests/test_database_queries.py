"""Test database queries for dealer and robot tools."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database.session import get_db
from app.database.models import Dealer, Robot, Industry
from sqlalchemy import select
import structlog

logger = structlog.get_logger()


async def create_sample_data():
    """Create sample dealers and robots for testing."""
    print("\n=== Creating Sample Data ===\n")

    async with get_db() as db:
        # Create sample dealers
        dealers = [
            Dealer(
                name="RoboTech Solutions SF",
                coverage="San Francisco Bay Area",
                address="123 Market St, San Francisco, CA 94105",
                phone="(415) 555-0123",
                email="sales@robotech-sf.com",
                website="https://robotech-sf.com",
                specialties=["AMRs", "AGVs", "Warehouse Automation"],
                zip_codes=["94105", "94102", "94103", "94104"],
                is_active=True
            ),
            Dealer(
                name="Industrial Automation Partners",
                coverage="Silicon Valley",
                address="456 Tech Blvd, San Jose, CA 95110",
                phone="(408) 555-0456",
                email="contact@indauto.com",
                website="https://indauto.com",
                specialties=["Robotic Arms", "Manufacturing", "Assembly Lines"],
                zip_codes=["95110", "95111", "95112"],
                is_active=True
            ),
            Dealer(
                name="AgriBot Supply",
                coverage="Central Valley",
                address="789 Farm Rd, Fresno, CA 93650",
                phone="(559) 555-0789",
                email="info@agribot.com",
                website="https://agribot.com",
                specialties=["Agricultural Drones", "Crop Management", "Harvest Automation"],
                zip_codes=["93650", "93651", "93652"],
                is_active=True
            ),
        ]

        for dealer in dealers:
            db.add(dealer)

        # Create sample robots
        robots = [
            Robot(
                name="Mobile Shelf AMR",
                manufacturer="Locus Robotics",
                category="AMR",
                description="Autonomous mobile robot for warehouse order picking and inventory management",
                use_case=Industry.LOGISTICS,
                payload="500 lbs",
                autonomy_level="Level 4",
                specifications={
                    "battery_life": "8 hours",
                    "charging_time": "1 hour",
                    "max_speed": "2 mph",
                    "dimensions": "24x36x48 inches"
                },
                lease_from="$1,299/month",
                lease_price_monthly=1299.0,
                image_url="https://example.com/mobile-shelf-amr.jpg",
                is_active=True
            ),
            Robot(
                name="Heavy Duty Pallet Bot",
                manufacturer="Fetch Robotics",
                category="AGV",
                description="Industrial pallet mover for heavy loads in warehouses and distribution centers",
                use_case=Industry.LOGISTICS,
                payload="3,000 lbs",
                autonomy_level="Level 4",
                specifications={
                    "battery_life": "10 hours",
                    "max_speed": "3 mph",
                    "turning_radius": "0 degrees",
                    "load_capacity": "3000 lbs"
                },
                lease_from="$2,499/month",
                lease_price_monthly=2499.0,
                image_url="https://example.com/pallet-bot.jpg",
                is_active=True
            ),
            Robot(
                name="Agricultural Spray Drone",
                manufacturer="DJI Agras",
                category="Drone",
                description="Precision crop spraying drone for efficient agricultural operations",
                use_case=Industry.AGRICULTURE,
                payload="10 gallons",
                autonomy_level="Level 3",
                specifications={
                    "flight_time": "20 minutes",
                    "coverage_rate": "40 acres/hour",
                    "spray_width": "20 feet",
                    "gps_accuracy": "2.5 cm"
                },
                lease_from="$899/month",
                lease_price_monthly=899.0,
                image_url="https://example.com/spray-drone.jpg",
                is_active=True
            ),
            Robot(
                name="Collaborative Assembly Arm",
                manufacturer="Universal Robots",
                category="Robotic Arm",
                description="Collaborative robot arm for assembly line operations and manufacturing",
                use_case=Industry.MANUFACTURING,
                payload="22 lbs",
                autonomy_level="Level 3",
                specifications={
                    "reach": "51.2 inches",
                    "repeatability": "±0.1 mm",
                    "degrees_of_freedom": "6",
                    "safety_features": ["force limiting", "collision detection"]
                },
                lease_from="$1,799/month",
                lease_price_monthly=1799.0,
                image_url="https://example.com/cobot-arm.jpg",
                is_active=True
            ),
        ]

        for robot in robots:
            db.add(robot)

        await db.commit()

        print(f"✅ Created {len(dealers)} dealers")
        print(f"✅ Created {len(robots)} robots\n")


async def test_dealer_lookup():
    """Test dealer lookup functionality."""
    print("\n=== Testing Dealer Lookup ===\n")

    from app.tools.dealer import DealerLookupTool

    tool = DealerLookupTool()

    # Test 1: Lookup by ZIP code
    print("Test 1: Lookup dealers in 94105...")
    result = tool._run(zip_code="94105")
    print(f"✅ Found {result['total_found']} dealers")
    for dealer in result['dealers']:
        print(f"  - {dealer['name']} (specialties: {', '.join(dealer['specialties'][:2])})")

    # Test 2: Lookup with specialty filter
    print("\nTest 2: Lookup dealers with 'warehouse' specialty...")
    result = tool._run(zip_code="94105", specialty="warehouse")
    print(f"✅ Found {result['total_found']} dealers")
    for dealer in result['dealers']:
        print(f"  - {dealer['name']}")

    # Test 3: Lookup in different area
    print("\nTest 3: Lookup dealers in 95110...")
    result = tool._run(zip_code="95110")
    print(f"✅ Found {result['total_found']} dealers")
    for dealer in result['dealers']:
        print(f"  - {dealer['name']}")


async def test_robot_search():
    """Test robot catalog search functionality."""
    print("\n=== Testing Robot Catalog Search ===\n")

    from app.tools.robot import RobotCatalogTool

    tool = RobotCatalogTool()

    # Test 1: Search by query
    print("Test 1: Search for 'warehouse' robots...")
    result = tool._run(query="warehouse")
    print(f"✅ Found {result['total_found']} robots")
    for robot in result['robots']:
        print(f"  - {robot['name']} by {robot['manufacturer']} ({robot['lease_from']})")

    # Test 2: Search by category
    print("\nTest 2: Search for AMR category...")
    result = tool._run(query="", category="AMR")
    print(f"✅ Found {result['total_found']} robots")
    for robot in result['robots']:
        print(f"  - {robot['name']} ({robot['category']})")

    # Test 3: Search by use case
    print("\nTest 3: Search for agriculture use case...")
    result = tool._run(query="", use_case="agriculture")
    print(f"✅ Found {result['total_found']} robots")
    for robot in result['robots']:
        print(f"  - {robot['name']} - {robot['description'][:60]}...")

    # Test 4: Combined search
    print("\nTest 4: Search for 'robot' in logistics...")
    result = tool._run(query="robot", use_case="logistics")
    print(f"✅ Found {result['total_found']} robots")
    for robot in result['robots']:
        print(f"  - {robot['name']} ({robot['payload']} payload)")


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("DATABASE QUERY TESTING")
    print("="*60)

    try:
        # Create sample data
        await create_sample_data()

        # Test dealer lookup
        await test_dealer_lookup()

        # Test robot search
        await test_robot_search()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
