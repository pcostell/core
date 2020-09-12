"""The tests for the Canary sensor platform."""
from homeassistant.components.canary import DOMAIN
from homeassistant.components.canary.sensor import (
    ATTR_AIR_QUALITY,
    STATE_AIR_QUALITY_ABNORMAL,
)
from homeassistant.const import ATTR_UNIT_OF_MEASUREMENT, PERCENTAGE, TEMP_CELSIUS
from homeassistant.setup import async_setup_component

from . import mock_device, mock_location, mock_reading

from tests.async_mock import patch
from tests.common import mock_registry


async def test_sensors_pro(hass, canary) -> None:
    """Test the creation and values of the sensors for Canary Pro."""
    assert await async_setup_component(hass, "persistent_notification", {})

    registry = mock_registry(hass)
    online_device_at_home = mock_device(20, "Dining Room", True, "Canary Pro")

    instance = canary.return_value
    instance.get_locations.return_value = [
        mock_location("Home", True, devices=[online_device_at_home]),
    ]

    instance.get_readings.return_value = [
        mock_reading("temperature", "21.12"),
        mock_reading("humidity", "50.46"),
        mock_reading("air_quality", "0.4"),
        mock_reading("battery", "70.4567"),
        mock_reading("wifi", "-57"),
    ]

    config = {DOMAIN: {"username": "test-username", "password": "test-password"}}
    with patch(
        "homeassistant.components.canary.alarm_control_panel.setup_platform",
        return_value=True,
    ), patch(
        "homeassistant.components.canary.camera.setup_platform",
        return_value=True,
    ):
        assert await async_setup_component(hass, DOMAIN, config)
        await hass.async_block_till_done()

    sensors = {
        "home_dining_room_temperature": (
            "20_temperature",
            "21.12",
            TEMP_CELSIUS,
            None,
            "mdi:thermometer",
        ),
        "home_dining_room_humidity": (
            "20_humidity",
            "50.46",
            PERCENTAGE,
            None,
            "mdi:water-percent",
        ),
        "home_dining_room_air_quality": (
            "20_air_quality",
            "0.4",
            None,
            None,
            "mdi:weather-windy",
        ),
    }

    for (sensor_id, data) in sensors.items():
        entity_entry = registry.async_get(f"sensor.{sensor_id}")
        assert entity_entry
        assert entity_entry.device_class == data[3]
        assert entity_entry.unique_id == data[0]

        state = hass.states.get(f"sensor.{sensor_id}")
        assert state
        assert state.attributes.get(ATTR_UNIT_OF_MEASUREMENT) == data[2]
        assert state.state == data[1]
        assert state.icon == data[4]

        if sensor_id == "home_dining_room_air_quality":
            assert (
                state.device_state_attributes[ATTR_AIR_QUALITY]
                == STATE_AIR_QUALITY_ABNORMAL
            )


async def test_sensors_flex(hass, canary) -> None:
    """Test the creation and values of the sensors for Canary Flex."""
    assert await async_setup_component(hass, "persistent_notification", {})

    registry = mock_registry(hass)
    online_device_at_home = mock_device(20, "Living Room", True, "Canary Flex")

    instance = canary.return_value
    instance.get_locations.return_value = [
        mock_location("Home", True, devices=[online_device_at_home]),
    ]

    instance.get_readings.return_value = [
        mock_reading("battery", "70.4567"),
        mock_reading("wifi", "-57"),
    ]

    config = {DOMAIN: {"username": "test-username", "password": "test-password"}}
    with patch(
        "homeassistant.components.canary.alarm_control_panel.setup_platform",
        return_value=True,
    ), patch(
        "homeassistant.components.canary.camera.setup_platform",
        return_value=True,
    ):
        assert await async_setup_component(hass, DOMAIN, config)
        await hass.async_block_till_done()

    sensors = {
        "home_dining_room_battery": (
            "20_battery",
            "70.4567",
            PERCENTAGE,
            None,
            "mdi:battery-70",
        ),
        "home_dining_room_wifi": ("20_wifi", "-57", "dBm", None, "mdi:wifi"),
    }

    for (sensor_id, data) in sensors.items():
        entity_entry = registry.async_get(f"sensor.{sensor_id}")
        assert entity_entry
        assert entity_entry.device_class == data[3]
        assert entity_entry.unique_id == data[0]

        state = hass.states.get(f"sensor.{sensor_id}")
        assert state
        assert state.attributes.get(ATTR_UNIT_OF_MEASUREMENT) == data[2]
        assert state.state == data[1]
        assert state.icon == data[4]
