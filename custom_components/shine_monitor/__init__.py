"""Initialize the Shine Monitor integration for Home Assistant."""

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from .const import DOMAIN
from .coordinator import ShineMonitorDataUpdateCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Shine Monitor component."""
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up Shine Monitor from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    coordinator = ShineMonitorDataUpdateCoordinator(
        hass,
        entry.data["username"],
        entry.data["password"],
        entry.data["company_key"],
        entry.data["plant_id"],
        entry.data["token"],
        entry.data["secret"],
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
