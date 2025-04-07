"""Poller for the personal door log API."""

import asyncio
import logging
from homeassistant.core import HomeAssistant

LOGGER = logging.getLogger(__name__)

class DoorLogPoller:
    """Poller for the personal door log API."""

    hass: HomeAssistant
    async_retrieve_personal_door_log = None
    interval: int = 300  # 5 minutes polling to reduce network load
    is_polling: bool = False

    def __init__(self,
                 hass: HomeAssistant,
                 poll_function,
                 interval=300):  # 5 minutes by default
        """Initialize the poller for the personal door log API."""
        self.hass = hass
        self.async_retrieve_personal_door_log = poll_function
        self.interval = interval
        self._task = None

    async def async_start(self):
        """Start polling the personal door log."""
        if self.async_retrieve_personal_door_log:
            if not self.is_polling:
                LOGGER.info("🔄 Polling user's personal door log every %s seconds (reduced frequency to avoid router issues)",
                           str(self.interval))
                self.is_polling = True
                self._task = asyncio.create_task(
                    self.async_retrieve_personal_door_log()) # type: ignore

    async def async_stop(self):
        """Stop polling the personal door log."""
        if self.is_polling and self._task:
            LOGGER.debug("🛑 Stop polling personal door log")
            self.is_polling = False
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                LOGGER.debug("Polling task cancelled")
            except Exception as e:
                LOGGER.error("Error when cancelling polling task: %s", str(e))
