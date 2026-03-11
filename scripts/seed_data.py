"""
TrainRadar - Seed Test Data
-----------------------------
Inserts sample train data into the database so we can
test the API endpoints with real responses.
Run with: python scripts/seed_data.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime, timezone, timedelta
from db.database import get_db_session
from db.models.models import TrainPosition, TripUpdate, ServiceAlert


async def seed_positions():
    """Insert sample train positions."""
    print("Seeding train positions...")

    positions = [
        TrainPosition(
            time=datetime.now(timezone.utc),
            train_id="IC123",
            trip_id="TRIP001",
            route_id="ROUTE_A",
            latitude=51.5074,
            longitude=-0.1278,
            speed_kmh=120.5,
            bearing=45.0,
            source="websocket",
        ),
        TrainPosition(
            time=datetime.now(timezone.utc) - timedelta(minutes=1),
            train_id="IC456",
            trip_id="TRIP002",
            route_id="ROUTE_B",
            latitude=53.4808,
            longitude=-2.2426,
            speed_kmh=95.0,
            bearing=180.0,
            source="gtfs-rt",
        ),
        TrainPosition(
            time=datetime.now(timezone.utc) - timedelta(minutes=2),
            train_id="IC789",
            trip_id="TRIP003",
            route_id="ROUTE_A",
            latitude=52.4862,
            longitude=-1.8904,
            speed_kmh=110.0,
            bearing=90.0,
            source="rest_api",
        ),
    ]

    async with get_db_session() as session:
        for position in positions:
            session.add(position)

    print(f"  ✅ Inserted {len(positions)} positions")


async def seed_trip_updates():
    """Insert sample delay updates."""
    print("Seeding trip updates...")

    updates = [
        TripUpdate(
            time=datetime.now(timezone.utc),
            trip_id="TRIP001",
            route_id="ROUTE_A",
            stop_id="STOP_01",
            stop_sequence=1,
            arrival_delay=120,    # 2 minutes late
            departure_delay=120,
            schedule_rel="SCHEDULED",
            source="gtfs-rt",
        ),
        TripUpdate(
            time=datetime.now(timezone.utc),
            trip_id="TRIP002",
            route_id="ROUTE_B",
            stop_id="STOP_03",
            stop_sequence=1,
            arrival_delay=-60,    # 1 minute early
            departure_delay=-60,
            schedule_rel="SCHEDULED",
            source="gtfs-rt",
        ),
        TripUpdate(
            time=datetime.now(timezone.utc),
            trip_id="TRIP003",
            route_id="ROUTE_A",
            stop_id="STOP_02",
            stop_sequence=2,
            arrival_delay=300,    # 5 minutes late
            departure_delay=300,
            schedule_rel="SCHEDULED",
            source="gtfs-rt",
        ),
    ]

    async with get_db_session() as session:
        for update in updates:
            session.add(update)

    print(f"  ✅ Inserted {len(updates)} trip updates")


async def seed_alerts():
    """Insert sample service alerts."""
    print("Seeding service alerts...")

    alerts = [
        ServiceAlert(
            alert_id="ALERT_001",
            effect="DELAY",
            cause="TECHNICAL_PROBLEM",
            header_text="Delays on Route A",
            description_text="Trains on Route A are delayed by up to 10 minutes due to a technical issue.",
            route_ids=["ROUTE_A"],
            stop_ids=["STOP_01", "STOP_02"],
            active_from=datetime.now(timezone.utc),
            active_until=datetime.now(timezone.utc) + timedelta(hours=2),
            source="gtfs-rt",
        ),
        ServiceAlert(
            alert_id="ALERT_002",
            effect="REDUCED_SERVICE",
            cause="STRIKE",
            header_text="Reduced service on Route B",
            description_text="Route B is running a reduced service today.",
            route_ids=["ROUTE_B"],
            stop_ids=[],
            active_from=datetime.now(timezone.utc),
            active_until=datetime.now(timezone.utc) + timedelta(hours=5),
            source="gtfs-rt",
        ),
    ]

    async with get_db_session() as session:
        for alert in alerts:
            session.add(alert)

    print(f"  ✅ Inserted {len(alerts)} alerts")


async def main():
    print("=" * 40)
    print("TrainRadar - Seeding Test Data")
    print("=" * 40)
    print()

    await seed_positions()
    await seed_trip_updates()
    await seed_alerts()

    print()
    print("=" * 40)
    print("✅ All test data inserted!")
    print()
    print("Now test your API:")
    print("  http://localhost:8000/positions")
    print("  http://localhost:8000/delays")
    print("  http://localhost:8000/alerts")
    print("=" * 40)


asyncio.run(main())