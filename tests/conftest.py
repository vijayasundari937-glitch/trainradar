"""
TrainRadar - Test Configuration
---------------------------------
Sets up the event loop for async tests.
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()