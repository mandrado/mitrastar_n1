#
# config_flow.py
#
# Versão Definitiva: Implementa o login com desafio-resposta MD5.
#

import logging
import voluptuous as vol
import requests
import re
import hashlib

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _blocking_validate_input(host, username, password):
    """Executa a validação de login com desafio-resposta MD5."""
    session = requests.Session()
    login_url = f"http://{host}/cgi-bin/login.cgi"
    headers = {'Referer': login_url}

    try:
        # --- PASSO 1: Obter a página de login para extrair o 'sid' ---
        _LOGGER.debug("Executando GET inicial para extrair o 'sid'...")
        get_response = session.get(login_url, timeout=10)
        get_response.raise_for_status()
        
        initial_html = get_response.content.decode("iso-8859-1", errors="ignore")
        
        # --- PASSO 2: Extrair o 'sid' usando Regex ---
        sid_match = re.search(r"var sid = '([a-f0-9]+)';", initial_html)
        if not sid_match:
            _LOGGER.error("Não foi possível encontrar o 'sid' na página de login.")
            return {"error": "invalid_auth"}
        sid = sid_match.group(1)
        _LOGGER.debug("Extraído 'sid': %s", sid)

        # --- PASSO 3: Calcular o hash da senha ---
        challenge_string = f"{password}:{sid}"
        hashed_password = hashlib.md5(challenge_string.encode('utf-8')).hexdigest()
        
        # --- PASSO 4: Montar e enviar o payload correto ---
        login_payload = {
            'Loginuser': username,
            'LoginPasswordValue': hashed_password,
            'acceptLoginIndex': '1'
        }
        
        _LOGGER.debug("Enviando payload de login com hash...")
        post_response = session.post(login_url, data=login_payload, headers=headers, timeout=10)
        post_response.raise_for_status()
        
        post_response_text = post_response.content.decode("iso-8859-1", errors="ignore")
        if "login" in post_response_text.lower() or not session.cookies:
            _LOGGER.error("Validação final falhou. Modem rejeitou o hash ou não enviou cookies.")
            return {"error": "invalid_auth"}

        _LOGGER.info("Validação de login com desafio-resposta bem-sucedida!")
        return {"title": f"MitraStar ({host})"}

    except requests.exceptions.RequestException as err:
        _LOGGER.error("Falha de conexão na validação: %s", err)
        return {"error": "cannot_connect"}

# O restante da classe MitraStarConfigFlow permanece o mesmo e está correto
class MitraStarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        errors = {}; 
        if user_input is not None:
            host = user_input[CONF_HOST]; username = user_input[CONF_USERNAME]; password = user_input[CONF_PASSWORD]
            info = await self.hass.async_add_executor_job(_blocking_validate_input, host, username, password)
            if "error" not in info:
                await self.async_set_unique_id(host); self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)
            errors["base"] = info["error"]
        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default="192.168.15.1"): str,
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)