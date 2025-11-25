# /config/custom_components/mitrastar_n1/binary_sensor.py

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Rastreia MACs já adicionados
    added_macs = set()
    
    @callback
    def _add_new_devices():
        """Adiciona sensores para novos dispositivos detectados."""
        current_macs = set(coordinator.data.get("devices", {}).keys())
        new_macs = current_macs - added_macs
        
        if new_macs:
            new_entities = [
                MitraStarDeviceSensor(coordinator, mac)
                for mac in new_macs
            ]
            async_add_entities(new_entities)
            added_macs.update(new_macs)
    
    # Adiciona dispositivos iniciais
    _add_new_devices()
    
    # Registra listener para futuras atualizações
    coordinator.async_add_listener(_add_new_devices)

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
        """Cria um dispositivo individual para cada cliente conectado."""
        device = self._device_data
        modem_mac = self.coordinator.data.get("modem_mac")
        
        if not device:
            return None
        
        hostname = device.get("hostname", "Unknown")
        if hostname == "Unknown" or not hostname:
            hostname = f"Device {self._mac[-8:].replace(':', '')}"
        
        return {
            "identifiers": {(DOMAIN, self._mac)},
            "name": hostname,
            "manufacturer": "Unknown",
            "model": "Network Device",
            "via_device": (DOMAIN, modem_mac) if modem_mac else None,
        }

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
