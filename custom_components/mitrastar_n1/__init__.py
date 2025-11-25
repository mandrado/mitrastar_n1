# /config/custom_components/mitrastar_n1/__init__.py

import logging
from datetime import timedelta
import re
import requests
import hashlib
import socket

# Home Assistant imports: guard so tests can run without Home Assistant installed
try:
    from homeassistant.core import HomeAssistant
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
    from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryAuthFailed
    _HAS_HA = True
except Exception:  # pragma: no cover - fallback for test environments
    # Define lightweight fallbacks so module can be imported in CI/local tests
    HomeAssistant = object
    ConfigEntry = object
    CONF_HOST = "host"
    CONF_USERNAME = "username"
    CONF_PASSWORD = "password"
    DataUpdateCoordinator = object
    UpdateFailed = Exception
    ConfigEntryNotReady = Exception
    ConfigEntryAuthFailed = Exception
    _HAS_HA = False

from .const import DOMAIN
from . import parsers

_LOGGER = logging.getLogger(__name__)

# Plataformas suportadas
PLATFORMS = ["binary_sensor", "sensor"]

# Configurações gerais
SCAN_INTERVAL = timedelta(seconds=60)
REQUEST_TIMEOUT = 30
BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Configura a integração a partir de uma entrada de configuração."""
    host = entry.data[CONF_HOST]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    coordinator = MitraStarCoordinator(hass, host, username, password)

    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady(
            f"Falha na primeira atualização de dados: {coordinator.last_exception}"
        )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Descarrega a entrada de configuração."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class MitraStarCoordinator(DataUpdateCoordinator):
    """Gerencia a busca de dados do modem MitraStar."""

    def __init__(self, hass, host, username, password):
        """Inicializa o coordinator."""
        self.host = host
        self.username = username
        self.password = password
        self._base_url = f"http://{host}"
        
        # Sessão persistente
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": BROWSER_USER_AGENT})
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    def _blocking_login(self):
        """Realiza o login no modem (executado no executor)."""
        login_url = f"{self._base_url}/cgi-bin/login.cgi"
        post_headers = {'Referer': login_url}

        try:
            # 1. Obter a página de login para pegar o 'sid' (salt)
            get_response = self.session.get(login_url, timeout=REQUEST_TIMEOUT)
            get_response.raise_for_status()
            initial_html = get_response.content.decode("iso-8859-1", errors="ignore")

            sid_match = re.search(r"var sid = '([a-f0-9]+)';", initial_html)
            if not sid_match:
                _LOGGER.error("Não foi possível encontrar o SID na página de login.")
                return False
            sid = sid_match.group(1)

            # 2. Calcular o hash da senha (senha:sid)
            challenge_string = f"{self.password}:{sid}"
            hashed_password = hashlib.md5(challenge_string.encode('utf-8')).hexdigest()

            # 3. Enviar POST de login
            login_payload = {
                'Loginuser': self.username,
                'LoginPasswordValue': hashed_password,
                'acceptLoginIndex': '1'
            }
            
            post_response = self.session.post(
                login_url, 
                data=login_payload, 
                headers=post_headers, 
                timeout=REQUEST_TIMEOUT
            )
            post_response_text = post_response.content.decode("iso-8859-1", errors="ignore")
            
            # Verifica sucesso (se redirecionou ou setou cookie)
            if "login" in post_response_text.lower() or not self.session.cookies:
                _LOGGER.error("Falha no login: Credenciais inválidas ou erro no processamento.")
                return False

            _LOGGER.info("Autenticação bem-sucedida com o modem.")
            return True

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Erro de conexão durante o login: %s", err)
            return False

    def _fetch_raw_socket(self, path):
        """
        Busca a URL usando sockets puros para contornar o erro de cabeçalho malformado do modem.
        Ignora completamente a validação HTTP do urllib3/requests.
        """
        try:
            _LOGGER.debug("Iniciando Raw Socket para: %s", path)
            
            # Prepara os cookies da sessão atual para enviar no socket
            cookies_str = "; ".join([f"{c.name}={c.value}" for c in self.session.cookies])
            
            # Monta a requisição HTTP manualmente
            request_data = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {self.host}\r\n"
                f"User-Agent: {BROWSER_USER_AGENT}\r\n"
                f"Connection: close\r\n"
                f"Referer: {self._base_url}/cgi-bin/sophia_index.cgi\r\n"
            )
            if cookies_str:
                request_data += f"Cookie: {cookies_str}\r\n"
            request_data += "\r\n"

            # Abre a conexão socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(REQUEST_TIMEOUT)
            sock.connect((self.host, 80))
            sock.sendall(request_data.encode())

            # Lê a resposta em chunks
            response_bytes = b""
            while True:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response_bytes += chunk
                except socket.timeout:
                    break
            sock.close()

            # Decodifica para string
            full_response = response_bytes.decode("iso-8859-1", errors="ignore")

            # TRUQUE: Encontrar onde começa o HTML real para ignorar headers quebrados
            # Procura por <!DOCTYPE ou <html
            start_index = full_response.find("<!DOCTYPE")
            if start_index == -1:
                start_index = full_response.find("<html")
            
            if start_index != -1:
                clean_html = full_response[start_index:]
                _LOGGER.debug("HTML extraído via Socket com sucesso (%d caracteres)", len(clean_html))
                return clean_html
            else:
                # Se não achou tag HTML, retorna tudo (fallback)
                _LOGGER.warning("Tag HTML não encontrada no socket, retornando resposta completa.")
                return full_response

        except Exception as e:
            _LOGGER.error("Erro no Raw Socket para %s: %s", path, e)
            return None

    def _blocking_fetch_url(self, path):
        """Método padrão de fetch para páginas que respeitam o protocolo HTTP."""
        url = self._base_url + path
        headers = {'Referer': f"{self._base_url}/cgi-bin/sophia_index.cgi"}
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
            response.raise_for_status()
            if "login" in response.url:
                raise UpdateFailed("Sessão expirada (redirecionado para login).")
            return response.content.decode("iso-8859-1", errors="ignore")
        except Exception as e:
            _LOGGER.warning("Erro no fetch padrão para %s: %s", path, e)
            raise

    async def _fetch_url_with_session(self, path):
        """Wrapper assíncrono para o fetch padrão."""
        return await self.hass.async_add_executor_job(self._blocking_fetch_url, path)

    async def _async_update_data(self):
        """Função principal de atualização de dados."""
        try:
            # Verifica se temos cookies (login feito), se não, tenta logar
            if not self.session.cookies:
                if not await self.hass.async_add_executor_job(self._blocking_login):
                    raise ConfigEntryAuthFailed("Falha na re-autenticação com o modem.")
            
            # 1. Busca Informações do Dispositivo (Página Problemática -> Raw Socket)
            _LOGGER.debug("Buscando about-power-box2.cgi via Socket...")
            about_html = await self.hass.async_add_executor_job(self._fetch_raw_socket, "/cgi-bin/about-power-box2.cgi")
            
            # 2. Busca outras páginas (Padrão requests)
            _LOGGER.debug("Buscando dhcp_client_list.cgi...")
            device_list_html = await self._fetch_url_with_session("/cgi-bin/dhcp_client_list.cgi")
            
            _LOGGER.debug("Buscando settings-wireless-network.cgi...")
            wifi_settings_html = await self._fetch_url_with_session("/cgi-bin/settings-wireless-network.cgi")
            
            _LOGGER.debug("Buscando settings-wireless-network-5g.cgi (5GHz)...")
            wifi_5g_html = None
            try:
                wifi_5g_html = await self._fetch_url_with_session("/cgi-bin/settings-wireless-network-5g.cgi")
            except Exception:
                _LOGGER.debug("Página 5GHz não disponível ou falha no fetch; continuará sem dados 5GHz.")
            
            _LOGGER.debug("Buscando settings-local-network.cgi...")
            local_network_html = await self._fetch_url_with_session("/cgi-bin/settings-local-network.cgi")
            
            # 3. Parsing dos dados
            device_info = self._parse_device_info(about_html)
            parsed_devices = self._parse_device_table(device_list_html)
            modem_mac = self._parse_with_regex(local_network_html, r"Endereço MAC:.*?([0-9a-fA-F:]{17})", str)
            wifi_data = self._parse_wifi_24ghz(wifi_settings_html)
            wifi_5g_data = self._parse_wifi_5ghz(wifi_5g_html) if wifi_5g_html else None

            # Consolida os dados (sem conectividade por enquanto)
            return {
                "device_info": device_info,
                "devices": parsed_devices,
                "modem_mac": modem_mac.upper() if modem_mac else None,
                "wifi_24ghz": wifi_data,
                "wifi_5ghz": wifi_5g_data,
            }
        except Exception as err:
            _LOGGER.error("Erro ao atualizar dados: %s", err)
            # Limpa cookies para forçar login na próxima tentativa
            self.session.cookies.clear()
            raise UpdateFailed(f"Erro ao atualizar dados: {err}") from err

    # --- MÉTODOS DE PARSING (REGEX) ---

    def _parse_device_info(self, html):
        """Extrai informações do dispositivo da página about."""
        if not html: return {}

        # Regex para capturar valores baseados nos IDs da tabela
        # Padrão: id='MLG_Vendor' ... </td><td>VALOR</td>
        def get_val(elem_id):
            # CORREÇÃO AQUI: Usando rf"..." (Raw F-String) para evitar SyntaxWarning
            regex = rf"id=['\"]{elem_id}['\"][^>]*>.*?</span>.*?</td>\s*<td>(.*?)</td>"
            val = self._parse_with_regex(html, regex, str, re.DOTALL)
            return val.strip() if val else None

        return {
            "fabricante": get_val("MLG_Vendor") or "MitraStar",
            "modelo": get_val("MLG_Model") or "GPT-2741GNAC-N1",
            "software_version": get_val("MLG_SW_Version"),
            "hardware_version": get_val("MLG_HW_Version"),
            "serial_number": get_val("MLG_Serial_Number"),
            "gpon_serial": get_val("MLG_GPON_Serial_Number"),
            "mac_wan": get_val("MLG_WAN_MAC_Address"),
            "mac_lan": get_val("MLG_LAN_MAC_Address"),
        }


    def _parse_wifi_24ghz(self, html):
        """Delegate parsing of 2.4GHz WiFi to parsers.py."""
        try:
            return parsers.parse_wifi_24ghz(html)
        except Exception as e:
            _LOGGER.exception("Erro ao parsear 2.4GHz via parsers.parse_wifi_24ghz: %s", e)
            return {}

    def _parse_wifi_5ghz(self, html):
        """Delegate parsing of 5GHz WiFi to parsers.py."""
        try:
            return parsers.parse_wifi_5ghz(html)
        except Exception as e:
            _LOGGER.exception("Erro ao parsear 5GHz via parsers.parse_wifi_5ghz: %s", e)
            return {}

    def _parse_device_table(self, html):
        """Extrai lista de dispositivos DHCP."""
        devices = {}
        if not html: return devices
        
        # Procura linhas da tabela
        table_rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)
        for row in table_rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.IGNORECASE)
            # Espera pelo menos 4 células: Hostname, MAC, IP, Lease
            if len(cells) >= 4:
                hostname = cells[0].strip()
                mac = cells[1].strip().upper()
                ip = cells[2].strip()
                lease = cells[3].strip()
                
                # Validação básica de MAC
                if mac and ":" in mac and len(mac) == 17:
                    devices[mac] = {
                        "hostname": hostname, 
                        "ip_address": ip, 
                        "lease_time": lease
                    }
        return devices

    def _parse_with_regex(self, html, regex, cast_type=str, flags=re.DOTALL):
        """Helper para extração segura com regex."""
        if not html: return None
        match = re.search(regex, html, flags)
        if match:
            try:
                return cast_type(match.group(1).strip())
            except (ValueError, IndexError):
                return None
        return None

    def _get_selected_value(self, html, select_name):
        """Try multiple strategies to find the selected value for a <select>.

        Strategies (in order):
        - <select name="..."> ... <option value="X" selected
        - <select name="..." value="X"
        - inspect the <select> block and find any <option[^>]*selected[^>]*value="X"
        - fallback: find a nearby label/td containing a known mode string
        Returns the raw value (string) or None.
        """
        if not html or not select_name:
            return None

        # 1) direct option with selected
        regex1 = rf'name="{select_name}"[^>]*>.*?<option[^>]*selected[^>]*value="([^"]+)"'
        val = self._parse_with_regex(html, regex1, str, re.DOTALL)
        if val:
            return val

        # 2) option with selected attribute maybe after value
        regex2 = rf'name="{select_name}"[^>]*>.*?<option[^>]*value="([^"]+)"[^>]*selected'
        val = self._parse_with_regex(html, regex2, str, re.DOTALL)
        if val:
            return val

        # 3) select itself carries value attribute
        regex3 = rf'name="{select_name}"[^>]*value="([^"]+)"'
        val = self._parse_with_regex(html, regex3, str, re.DOTALL)
        if val:
            return val

        # 4) locate the select block and search for an option marked by 'selected' without value
        regex4 = rf'name="{select_name}"[^>]*>(.*?)</select>'
        block = self._parse_with_regex(html, regex4, str, re.DOTALL)
        if block:
            m = re.search(r'value="([^"]+)"[^>]*selected', block)
            if m:
                return m.group(1)

        # 5) fallback: try to extract visible text for a nearby label (common layouts)
        regex5 = rf'{select_name}[^>]*>.*?</select>.*?</td>\s*<td[^>]*>([^<]+)</td>'
        val = self._parse_with_regex(html, regex5, str, re.DOTALL)
        if val:
            return val

        return None
