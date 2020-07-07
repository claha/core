"""Support for getting instrument data from avanza.se."""
from datetime import timedelta
import logging

import pyavanza

from homeassistant.const import CONF_ID
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=60)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Avanza Stock sensor."""
    instrument_type = pyavanza.InstrumentType.STOCK
    instrument_id = entry.data[CONF_ID]
    session = async_create_clientsession(hass)
    async_add_entities([AvanzaSensor(instrument_type, instrument_id, session)], True)


class AvanzaSensor(Entity):
    """Representation of a Avanza sensor."""

    def __init__(
        self, instrument_type, instrument_id, session,
    ):
        """Initialize a Avanza sensor."""
        self._instrument_type = instrument_type
        self._instrument_id = instrument_id
        self._session = session
        self._name = f"Avanza {instrument_type.value} {instrument_id} "
        self._icon = "mdi:cash"
        self._state = 0
        self._unit_of_measurement = ""

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def unique_id(self) -> str:
        """Return a unique id."""
        return f"{self._instrument_id}"

    async def async_update(self):
        """Update."""
        if self._instrument_type == pyavanza.InstrumentType.STOCK:
            stock = await pyavanza.get_stock_async(self._session, self._instrument_id)
            self._state = stock.last_price
            self._unit_of_measurement = stock.currency
