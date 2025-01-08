import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import hashlib
import time
import aiohttp

from .const import DOMAIN


class ShineMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Shine Monitor."""

    VERSION = 1

    def __init__(self):
        """Initialize flow."""
        self.plants = []
        self.auth_info = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                plants, token, secret = await self._authenticate(
                    user_input["username"],
                    user_input["password"],
                    user_input["company_key"],
                )

                self.auth_info = {
                    "username": user_input["username"],
                    "password": user_input["password"],
                    "company_key": user_input["company_key"],
                    "token": token,
                    "secret": secret,
                }
                self.plants = plants

                return await self.async_step_plant()

            except Exception as e:
                errors["base"] = str(e)

        data_schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Required("company_key"): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_plant(self, user_input=None):
        """Handle plant selection."""
        errors = {}

        if user_input is not None:
            selected_plant = next(
                (
                    plant
                    for plant in self.plants
                    if str(plant["pid"]) == user_input["plant"]
                ),
                None,
            )

            if selected_plant:
                return self.async_create_entry(
                    title=f"Shine Monitor - {selected_plant['name']}",
                    data={
                        **self.auth_info,
                        "plant_id": selected_plant["pid"],
                        "plant_name": selected_plant["name"],
                    },
                )

        plant_schema = vol.Schema(
            {
                vol.Required("plant"): vol.In(
                    {str(plant["pid"]): plant["name"] for plant in self.plants}
                )
            }
        )

        return self.async_show_form(
            step_id="plant", data_schema=plant_schema, errors=errors
        )

    async def _authenticate(self, username, password, company_key):
        """Authenticate and get plants list."""
        salt = str(int(time.time() * 1000))
        hashed_password = hashlib.sha1(password.encode("utf-8")).hexdigest()
        auth_action = f"&action=auth&usr={username}&company-key={company_key}"
        auth_sign_string = salt + hashed_password + auth_action
        auth_sign = hashlib.sha1(auth_sign_string.encode("utf-8")).hexdigest()
        auth_url = f"http://api.shinemonitor.com/public/?sign={auth_sign}&salt={salt}{auth_action}"

        async with aiohttp.ClientSession() as session:
            try:
                response = await session.get(auth_url)
                if response.status == 200:
                    data = await response.json()
                    if data.get("err") == 0:
                        token = data["dat"]["token"]
                        secret = data["dat"]["secret"]

                        # Fetch plants list
                        plants = await self._fetch_plants(token, secret)
                        return plants, token, secret
                    else:
                        raise Exception(f"Authentication failed: {data.get('desc')}")
                else:
                    raise Exception(
                        f"Authentication request failed with status {response.status}"
                    )
            except Exception as e:
                raise Exception(f"Error during authentication: {str(e)}")

    async def _fetch_plants(self, token, secret):
        """Fetch plants list."""
        salt = str(int(time.time() * 1000))
        action = "&action=queryPlants"
        sign_string = salt + secret + token + action
        sign = hashlib.sha1(sign_string.encode("utf-8")).hexdigest()
        url = f"http://api.shinemonitor.com/public/?sign={sign}&token={token}&salt={salt}{action}"

        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            if response.status == 200:
                data = await response.json()
                if data.get("err") == 0:
                    return data["dat"]["plant"]
                else:
                    raise Exception(f"Failed to fetch plants: {data.get('desc')}")
            else:
                raise Exception(f"Plants request failed with status {response.status}")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ShineMonitorOptionsFlowHandler(config_entry)


class ShineMonitorOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Shine Monitor options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "username", default=self.config_entry.data.get("username")
                    ): str,
                    vol.Required(
                        "password", default=self.config_entry.data.get("password")
                    ): str,
                    vol.Required(
                        "company_key", default=self.config_entry.data.get("company_key")
                    ): str,
                }
            ),
        )
