"""Sensor platform for akuvox."""
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers import storage
from homeassistant.helpers.entity import DeviceInfo

from .api import AkuvoxApiClient
from .coordinator import AkuvoxDataUpdateCoordinator
from .const import (
    DOMAIN,
    LOGGER,
    NAME,
    VERSION,
    DATA_STORAGE_KEY
)
from .entity import AkuvoxEntity

async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the temporary door key platform."""
    coordinator: AkuvoxDataUpdateCoordinator
    for _key, value in hass.data[DOMAIN].items():
        coordinator = value
    client = coordinator.client
    store = storage.Store(hass, 1, DATA_STORAGE_KEY)
    device_data: dict = await store.async_load() # type: ignore
    door_keys_data = device_data["door_keys_data"]

    entities = []
    for door_key_data in door_keys_data:
        key_id = door_key_data["key_id"]
        description = door_key_data["description"]
        key_code=door_key_data["key_code"]
        
        # Try multiple date formats to handle different API responses
        begin_time_str = str(door_key_data["begin_time"])
        end_time_str = str(door_key_data["end_time"])
        
        # Try to parse date with multiple formats
        begin_time = end_time = None
        date_formats = [
            "%d-%m-%Y %H:%M:%S",  # Original format
            "%Y-%m-%d %H:%M:%S",  # New format observed in error logs
            "%Y/%m/%d %H:%M:%S",  # Another possible format
        ]
        
        for format in date_formats:
            try:
                begin_time = datetime.strptime(begin_time_str, format)
                end_time = datetime.strptime(end_time_str, format)
                LOGGER.debug("✅ Successfully parsed dates with format: %s", format)
                break
            except ValueError:
                continue
        
        if begin_time is None or end_time is None:
            LOGGER.error("❌ Could not parse dates for key %s: %s and %s", 
                       key_id, begin_time_str, end_time_str)
            continue  # Skip this door key if dates can't be parsed
        
        allowed_times=door_key_data["allowed_times"]
        access_times=door_key_data["access_times"]
        qr_code_url=door_key_data["qr_code_url"]

        entities.append(
            AkuvoxTemporaryDoorKey(
                client=client,
                entry=entry,
                key_id=key_id,
                description=description,
                key_code=key_code,
                begin_time=begin_time,
                end_time=end_time,
                allowed_times=allowed_times,
                access_times=access_times,
                qr_code_url=qr_code_url,
            )
        )

    async_add_devices(entities)

class AkuvoxTemporaryDoorKey(SensorEntity, AkuvoxEntity):
    """Akuvox temporary door key class."""

    def __init__(
        self,
        client: AkuvoxApiClient,
        entry,
        key_id: str,
        description: str,
        key_code: str,
        begin_time: datetime,
        end_time: datetime,
        allowed_times: int,
        access_times: int,
        qr_code_url) -> None:
        """Initialize the Akuvox door relay class."""
        super(SensorEntity, self).__init__(client=client, entry=entry)
        AkuvoxEntity.__init__(
            self=self,
            client=client,
            entry=entry
        )
        self.client = client
        self.key_id = key_id
        self.description = description
        self.key_code = key_code
        self.begin_time = begin_time
        self.end_time = end_time
        self.allowed_times = allowed_times
        self.access_times = access_times
        self.qr_code_url = qr_code_url
        self.expired = False

        name = f"{self.description} {self.key_id}".strip()
        self._attr_unique_id = name
        self._attr_name = name
        self._attr_key_code = key_code

        self._attr_extra_state_attributes = self.to_dict()

        LOGGER.debug("Adding temporary door key '%s'", self._attr_unique_id)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "Temporary Keys")},  # type: ignore
            name="Temporary Keys",
            model=VERSION,
            manufacturer=NAME,
        )

    def is_key_active(self):
        """Check if the key is currently active based on the begin_time and end_time."""
        current_time = datetime.now()
        return self.begin_time <= current_time <= self.end_time

    def to_dict(self):
        """Convert the object to a dictionary for easy serialization."""
        return {
            'key_id': self.key_id,
            'description': self.description,
            'key_code': self.key_code,
            'enabled': self.is_key_active(),
            'begin_time': self.begin_time,
            'end_time': self.end_time,
            'access_times': self.access_times,
            'allowed_times': self.allowed_times,
            'qr_code_url': self.qr_code_url,
            'expired': not self.is_key_active()
        }
