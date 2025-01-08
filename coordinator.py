import logging
import aiohttp
import hashlib
import time
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=5)


class ShineMonitorDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Shine Monitor data."""

    def __init__(self, hass, username, password, company_key, plant_id, token, secret):
        """Initialize the data update coordinator."""
        self.username = username
        self.password = password
        self.company_key = company_key
        self.plant_id = plant_id
        self.token = token
        self.secret = secret
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)

    async def _async_update_data(self):
        """Fetch data from the Shine Monitor API."""
        current_power = await self._fetch_current_power()
        total_power = await self._fetch_total_power()
        profit_data = await self._fetch_profit_data()

        return {
            "current_power": current_power,
            "total_energy": total_power,
            "profit": profit_data.get("profit", 0),
            "coal": profit_data.get("coal", 0),
            "co2": profit_data.get("co2", 0),
            "so2": profit_data.get("so2", 0),
        }

    async def _fetch_current_power(self):
        """Fetch the current active output power from the Shine Monitor API."""
        data_salt = str(int(time.time() * 1000))
        data_action = (
            f"&action=queryPlantsActiveOuputPowerCurrent&plantid={self.plant_id}"
        )
        data_sign_string = data_salt + self.secret + self.token + data_action
        data_sign = hashlib.sha1(data_sign_string.encode("utf-8")).hexdigest()
        data_url = f"http://api.shinemonitor.com/public/?sign={data_sign}&token={self.token}&salt={data_salt}{data_action}"

        async with aiohttp.ClientSession() as session:
            try:
                response = await session.get(data_url)
                if response.status == 200:
                    data = await response.json()
                    if data.get("err") == 0:
                        return float(data["dat"]["outputPower"])
                    elif data.get("desc") == "ERR_NO_RECORD":
                        return 0
                    else:
                        raise UpdateFailed(f"Data retrieval failed: {data.get('desc')}")
                else:
                    raise UpdateFailed(
                        f"Data request failed with status code {response.status}"
                    )
            except Exception as err:
                raise UpdateFailed(f"Error during data retrieval: {err}")

    async def _fetch_total_power(self):
        """Fetch the total energy production from the Shine Monitor API."""
        data_salt = str(int(time.time() * 1000))
        data_action = f"&action=queryPlantEnergyDay&plantid={self.plant_id}"
        data_sign_string = data_salt + self.secret + self.token + data_action
        data_sign = hashlib.sha1(data_sign_string.encode("utf-8")).hexdigest()
        data_url = f"http://api.shinemonitor.com/public/?sign={data_sign}&token={self.token}&salt={data_salt}{data_action}"

        async with aiohttp.ClientSession() as session:
            try:
                response = await session.get(data_url)
                if response.status == 200:
                    data = await response.json()
                    if data.get("err") == 0:
                        return float(data["dat"]["energy"])
                    elif data.get("desc") == "ERR_NO_RECORD":
                        return 0
                    else:
                        raise UpdateFailed(f"Data retrieval failed: {data.get('desc')}")
                else:
                    raise UpdateFailed(
                        f"Data request failed with status code {response.status}"
                    )
            except Exception as err:
                raise UpdateFailed(f"Error during data retrieval: {err}")

    async def _fetch_profit_data(self):
        """Fetch profit and environmental data."""
        data_salt = str(int(time.time() * 1000))
        data_action = f"&action=queryPlantsProfitOneDay&plantid={self.plant_id}"
        data_sign_string = data_salt + self.secret + self.token + data_action
        data_sign = hashlib.sha1(data_sign_string.encode("utf-8")).hexdigest()
        data_url = f"http://api.shinemonitor.com/public/?sign={data_sign}&token={self.token}&salt={data_salt}{data_action}"

        async with aiohttp.ClientSession() as session:
            try:
                response = await session.get(data_url)
                if response.status == 200:
                    data = await response.json()
                    if data.get("err") == 0:
                        plant_data = data["dat"]["plant"][0]
                        return {
                            "profit": float(plant_data["profit"]),
                            "coal": float(plant_data["coal"]),
                            "co2": float(plant_data["co2"]),
                            "so2": float(plant_data["so2"]),
                        }
                    else:
                        raise UpdateFailed(f"Data retrieval failed: {data.get('desc')}")
                else:
                    raise UpdateFailed(
                        f"Data request failed with status code {response.status}"
                    )
            except Exception as err:
                raise UpdateFailed(f"Error during data retrieval: {err}")
