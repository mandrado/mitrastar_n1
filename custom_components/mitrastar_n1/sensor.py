# /config/custom_components/mitrastar_n1/sensor.py

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
# No runtime monkey-patch imports here; parsing is implemented in __init__.py

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        MitraStarDeviceInfo(coordinator),
        MitraStarWifi(coordinator),   # 2.4GHz
        MitraStarWifi5G(coordinator), # 5GHz (NOVO)
    ]

    async_add_entities(sensors)

class MitraStarDeviceInfo(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "MitraStar Modem Info"
        self._attr_unique_id = f"{coordinator.host}_device_info"
        self._attr_icon = "mdi:router-wireless"

    @property
    def state(self):
        return self.coordinator.data.get("device_info", {}).get("modelo", "Desconhecido")

    @property
    def extra_state_attributes(self):
        return self.coordinator.data.get("device_info", {})

class MitraStarWifi(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "MitraStar WiFi 2.4GHz"
        self._attr_unique_id = f"{coordinator.host}_wifi_24"
        self._attr_icon = "mdi:wifi"

    @property
    def state(self):
        data = self.coordinator.data.get("wifi_24ghz", {})
        return "Ativo" if data.get("enabled") else "Inativo"

    @property
    def extra_state_attributes(self):
        return self.coordinator.data.get("wifi_24ghz", {})


class MitraStarWifi5G(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "MitraStar WiFi 5GHz"
        self._attr_unique_id = f"{coordinator.host}_wifi_5"
        self._attr_icon = "mdi:wifi"

    @property
    def state(self):
        data = self.coordinator.data.get("wifi_5ghz") or self.coordinator.data.get("wifi_24ghz") or {}
        enabled = data.get("enabled")
        if enabled is None:
            return "Desconhecido"
        return "Ativo" if enabled else "Inativo"

    @property
    def extra_state_attributes(self):
        data = None
        if "wifi_5ghz" in self.coordinator.data and self.coordinator.data.get("wifi_5ghz"):
            data = self.coordinator.data.get("wifi_5ghz")
        else:
            # fallback to 2.4GHz data if 5GHz not present
            fallback = self.coordinator.data.get("wifi_24ghz") or {}
            if fallback:
                data = dict(fallback)
                data["_note"] = "5GHz data not present; using 2.4GHz fallback"
        return data or {}
