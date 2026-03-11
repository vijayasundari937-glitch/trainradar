import sys
import os

# Add the project root to Python's path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import aiohttp
from ingestion.sources.rest_poller import fetch_schedules


async def main():
    print("Testing REST poller...")
    print("-" * 40)

    async with aiohttp.ClientSession() as session:
        schedules = await fetch_schedules(session)

    print(f"Fetched {len(schedules)} schedules:")
    print()

    for i, schedule in enumerate(schedules, 1):
        print(f"Schedule {i}:")
        print(f"  Trip ID:    {schedule['trip_id']}")
        print(f"  Route ID:   {schedule['route_id']}")
        print(f"  Headsign:   {schedule['headsign']}")
        print(f"  Stop ID:    {schedule['stop_id']}")
        print(f"  Departure:  {schedule['departure_time']}")
        print()

    print("Done!")


asyncio.run(main())