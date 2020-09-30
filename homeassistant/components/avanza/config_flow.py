"""Config flow for Avanza integration."""
import logging

import pyavanza
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

INSTRUMENT_SEARCH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(
            "instrument_type", default=pyavanza.InstrumentType.ANY.value
        ): vol.In(
            [
                pyavanza.InstrumentType.ANY.value,
                pyavanza.InstrumentType.BOND.value,
                pyavanza.InstrumentType.CERTIFICATE.value,
                pyavanza.InstrumentType.CONVERTIBLE.value,
                pyavanza.InstrumentType.EQUITY_LINKED_BOND.value,
                pyavanza.InstrumentType.EXCHANGE_TRADED_FUND.value,
                pyavanza.InstrumentType.FUND.value,
                pyavanza.InstrumentType.FUTURE_FORWARD.value,
                pyavanza.InstrumentType.INDEX.value,
                pyavanza.InstrumentType.OPTION.value,
                pyavanza.InstrumentType.PREMIUM_BOND.value,
                pyavanza.InstrumentType.RIGHT.value,
                pyavanza.InstrumentType.STOCK.value,
                pyavanza.InstrumentType.SUBSCRIPTION_OPTION.value,
                pyavanza.InstrumentType.WARRANT.value,
            ]
        ),
        vol.Required("instrument_query"): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Avanza."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        return await self.async_step_instrument_search()

    async def async_step_instrument_search(self, user_input=None):
        """Handle the search for an instrument."""
        errors = {}
        if user_input is not None:
            try:
                session = aiohttp_client.async_get_clientsession(self.hass)
                query = user_input["instrument_query"]
                instrument = pyavanza.InstrumentType[user_input["instrument_type"]]
                instruments = await pyavanza.search_async(
                    session,
                    query,
                    limit=10,
                    instrument=instrument,
                )
                return await self.async_step_instrument_select(user_input=instruments)
            except pyavanza.AvanzaResponseError:
                errors["base"] = "response_error"
            except pyavanza.AvanzaRequestError:
                errors["base"] = "request_error"
            except pyavanza.AvanzaParseError:
                errors["base"] = "parse_error"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="instrument_search",
            data_schema=INSTRUMENT_SEARCH_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_instrument_select(self, user_input):
        """Handle the selection of an instrument."""
        errors = {}
        if isinstance(user_input, list):
            instruments = user_input
            data_schema = vol.Schema(
                {
                    vol.Required("instrument"): vol.In(
                        [instrument.name for instrument in instruments]
                    )
                }
            )
            return self.async_show_form(
                step_id="instrument_select", data_schema=data_schema, errors=errors
            )
        else:
            instrument = user_input
            return self.async_create_entry(title=instrument, data={})
