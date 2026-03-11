"""
TrainRadar - Unit Tests for Validators
----------------------------------------
Tests that our Pydantic schemas correctly
validate and reject train data.
"""

import pytest
from etl.validators.schemas import (
    TrainPositionSchema,
    TripUpdateSchema,
    ServiceAlertSchema,
)


# ── TrainPositionSchema Tests ─────────────────────────────────────────────────

def test_valid_position():
    """A complete valid position should pass validation."""
    data = {
        "train_id":  "IC123",
        "latitude":  51.5074,
        "longitude": -0.1278,
        "source":    "gtfs-rt",
    }
    position = TrainPositionSchema(**data)
    assert position.train_id == "IC123"
    assert position.latitude == 51.5074
    assert position.longitude == -0.1278


def test_position_optional_fields():
    """Optional fields should default to None."""
    data = {
        "train_id":  "IC123",
        "latitude":  51.5074,
        "longitude": -0.1278,
    }
    position = TrainPositionSchema(**data)
    assert position.speed_kmh is None
    assert position.bearing is None
    assert position.trip_id is None


def test_invalid_latitude_too_high():
    """Latitude above 90 should fail validation."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        TrainPositionSchema(
            train_id="IC123",
            latitude=91.0,      # invalid — max is 90
            longitude=-0.1278,
        )


def test_invalid_latitude_too_low():
    """Latitude below -90 should fail validation."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        TrainPositionSchema(
            train_id="IC123",
            latitude=-91.0,     # invalid — min is -90
            longitude=-0.1278,
        )


def test_invalid_longitude_too_high():
    """Longitude above 180 should fail validation."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        TrainPositionSchema(
            train_id="IC123",
            latitude=51.5074,
            longitude=181.0,    # invalid — max is 180
        )


def test_invalid_longitude_too_low():
    """Longitude below -180 should fail validation."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        TrainPositionSchema(
            train_id="IC123",
            latitude=51.5074,
            longitude=-181.0,   # invalid — min is -180
        )


def test_position_missing_train_id():
    """Missing train_id should fail validation."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        TrainPositionSchema(
            latitude=51.5074,
            longitude=-0.1278,
        )


# ── TripUpdateSchema Tests ────────────────────────────────────────────────────

def test_valid_trip_update():
    """A valid trip update should pass validation."""
    data = {
        "trip_id":       "TRIP001",
        "route_id":      "ROUTE_A",
        "stop_id":       "STOP_01",
        "arrival_delay": 120,
    }
    update = TripUpdateSchema(**data)
    assert update.trip_id == "TRIP001"
    assert update.arrival_delay == 120


def test_trip_update_negative_delay():
    """Negative delay means train is early — should be valid."""
    data = {
        "trip_id":       "TRIP001",
        "arrival_delay": -60,   # 1 minute early
    }
    update = TripUpdateSchema(**data)
    assert update.arrival_delay == -60


def test_trip_update_missing_trip_id():
    """Missing trip_id should fail validation."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        TripUpdateSchema(arrival_delay=120)


# ── ServiceAlertSchema Tests ──────────────────────────────────────────────────

def test_valid_alert():
    """A valid service alert should pass validation."""
    data = {
        "alert_id":    "ALERT_001",
        "effect":      "DELAY",
        "header_text": "Delays on Route A",
        "route_ids":   ["ROUTE_A"],
    }
    alert = ServiceAlertSchema(**data)
    assert alert.alert_id == "ALERT_001"
    assert alert.effect == "DELAY"


def test_alert_missing_alert_id():
    """Missing alert_id should fail validation."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ServiceAlertSchema(effect="DELAY")