import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import aiohttp
from ingestion.sources.tfl_connector import fetch_arrivals, fetch_line_status
from config.settings import settings


async def main():
    print("=" * 50)
    print("TrainRadar - TfL Live Data Test")
    print("=" * 50)
    print()

    async with aiohttp.ClientSession() as session:

        # Test 1 — Live arrivals
        print(f"Fetching live arrivals for {settings.tfl_line} line...")
        print(f"Stop: {settings.tfl_stop_id}")
        print("-" * 50)

        arrivals = await fetch_arrivals(
            session,
            settings.tfl_line,
            settings.tfl_stop_id
        )

        if arrivals:
            # Sort by time to station
            arrivals.sort(key=lambda x: x.get("timeToStation", 999))
            print(f"Got {len(arrivals)} real arrivals!")
            print()
            for arrival in arrivals[:5]:
                mins = arrival.get("timeToStation", 0) // 60
                secs = arrival.get("timeToStation", 0) % 60
                print(f"  Train:       {arrival.get('vehicleId')}")
                print(f"  Destination: {arrival.get('destinationName')}")
                print(f"  Arrives in:  {mins}m {secs}s")
                print(f"  Platform:    {arrival.get('platformName')}")
                print(f"  Location:    {arrival.get('currentLocation')}")
                print()
        else:
            print("No arrivals found right now.")
        print()

        # Test 2 — Line status
        print(f"Fetching {settings.tfl_line} line status...")
        print("-" * 50)

        statuses = await fetch_line_status(session, settings.tfl_line)

        for status in statuses:
            for s in status.get("lineStatuses", []):
                print(f"  Status: {s.get('statusSeverityDescription')}")
                if s.get("reason"):
                    print(f"  Reason: {s.get('reason')}")
        print()
        print("✅ TfL connector working!")


asyncio.run(main())