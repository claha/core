"""The tests for the Modbus switch component."""
from datetime import timedelta
import logging

import pytest

from homeassistant.components.modbus.const import CALL_TYPE_COIL, CONF_COILS
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import CONF_NAME, CONF_SLAVE, STATE_OFF, STATE_ON

from .conftest import run_base_read_test, setup_base_test

_LOGGER = logging.getLogger(__name__)


async def run_sensor_test(hass, use_mock_hub, value, expected):
    """Run test for given config."""
    switch_name = "modbus_test_switch"
    scan_interval = 5
    entity_id, now, device = await setup_base_test(
        switch_name,
        hass,
        use_mock_hub,
        {
            CONF_COILS: [
                {CONF_NAME: switch_name, CALL_TYPE_COIL: 1234, CONF_SLAVE: 1},
            ]
        },
        SWITCH_DOMAIN,
        scan_interval,
    )

    await run_base_read_test(
        entity_id,
        hass,
        use_mock_hub,
        CALL_TYPE_COIL,
        value,
        expected,
        now + timedelta(seconds=scan_interval + 1),
    )


@pytest.mark.parametrize(
    "regs,expected",
    [
        (
            [0x00],
            STATE_OFF,
        ),
        (
            [0xFF],
            STATE_ON,
        ),
        (
            [0x01],
            STATE_ON,
        ),
    ],
)
async def test_coil_switch(hass, mock_hub, regs, expected):
    """Test reading of switch coil."""
    await run_sensor_test(
        hass,
        mock_hub,
        regs,
        expected,
    )
