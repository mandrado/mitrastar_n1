# /config/custom_components/mitrastar_n1/binary_sensor.py

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Adiciona sensores para todos os dispositivos encontrados
    entities = [
        MitraStarDeviceSensor(coordinator, mac)
        for mac in coordinator.data.get("devices", {}).keys()
    ]
    
    async_add_entities(entities)

class MitraStarDeviceSensor(CoordinatorEntity, BinarySensorEntity):
    """Sensor para dispositivos conectados ao modem."""
    _attr_has_entity_name = True

    def __init__(self, coordinator, mac_address: str):
        super().__init__(coordinator)
        self._mac = mac_address
        self._attr_unique_id = mac_address
        self._attr_device_class = "presence"

    @property
    def device_info(self):
        modem_mac = self.coordinator.data.get("modem_mac")
        if not modem_mac:
            return None
        return {"via_device": (DOMAIN, modem_mac)}

    @property
    def _device_data(self):
        return self.coordinator.data.get("devices", {}).get(self._mac)

    @property
    def name(self):
        """Retorna o nome do dispositivo, usando o hostname se disponível."""
        if self._device_data and self._device_data.get("hostname") != "Unknown":
            return self._device_data.get("hostname")
        return f"Dispositivo {self._mac.replace(':', '')[-6:]}"

    @property
    def is_on(self):
        """Retorna True se o dispositivo está no dicionário de dispositivos do coordinator."""
        return self._mac in self.coordinator.data.get("devices", {})

    @property
    def extra_state_attributes(self):
        """Retorna os atributos ricos do dispositivo."""
        if not self.is_on or not self._device_data:
            return None
        return {
            "hostname": self._device_data.get("hostname"),
            "ip_address": self._device_data.get("ip_address"),
            "lease_time": self._device_data.get("lease_time"),
            "mac_address": self._mac
        }