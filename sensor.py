import logging
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
    UnitOfMass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Shine Monitor sensor platform from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            CurrentSolarPowerSensor(coordinator),
            TotalSolarProductionSensor(coordinator),
            ProfitSensor(coordinator),
            CoalSavingSensor(coordinator),
            CO2ReductionSensor(coordinator),
            SO2ReductionSensor(coordinator),
        ]
    )


class ProfitSensor(CoordinatorEntity, SensorEntity):
    """Representation of profit sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Solar Profit"
        self._attr_unique_id = f"{coordinator.plant_id}_profit"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = "₹"

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("profit")


class CoalSavingSensor(CoordinatorEntity, SensorEntity):
    """Representation of coal saving sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Coal Saving"
        self._attr_unique_id = f"{coordinator.plant_id}_coal"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("coal")


class CO2ReductionSensor(CoordinatorEntity, SensorEntity):
    """Representation of CO2 reduction sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "CO2 Reduction"
        self._attr_unique_id = f"{coordinator.plant_id}_co2"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("co2")


class SO2ReductionSensor(CoordinatorEntity, SensorEntity):
    """Representation of SO2 reduction sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "SO2 Reduction"
        self._attr_unique_id = f"{coordinator.plant_id}_so2"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("so2")


class CurrentSolarPowerSensor(CoordinatorEntity, SensorEntity):
    """Representation of current solar power sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Current Solar Production"
        self._attr_unique_id = f"{coordinator.plant_id}_current_power"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfPower.KILO_WATT

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("current_power")


class TotalSolarProductionSensor(CoordinatorEntity, SensorEntity):
    """Representation of total solar production sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Total Solar Production"
        self._attr_unique_id = f"{coordinator.plant_id}_total_energy"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("total_energy")
