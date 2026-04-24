"""Sensor voor Financieel Beheer – toont het aantal te reviewen transacties."""
import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, ATTR_TOTAL_TRANSACTIONS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([FinanceReviewSensor(coordinator, entry)])


class FinanceReviewSensor(CoordinatorEntity, SensorEntity):
    """Sensor die het aantal transacties weergeeft dat review nodig heeft."""

    _attr_icon = "mdi:bank-check"
    _attr_native_unit_of_measurement = "transacties"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_name = "Te reviewen transacties"

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_needs_review"

    @property
    def native_value(self) -> int | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("needs_review")

    @property
    def extra_state_attributes(self) -> dict:
        if self.coordinator.data is None:
            return {}
        return {
            ATTR_TOTAL_TRANSACTIONS: self.coordinator.data.get("total"),
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Financieel Beheer",
            manufacturer="ha-finance-addon",
            model="Finance Manager",
            configuration_url=self._entry.data.get(CONF_URL),
        )
