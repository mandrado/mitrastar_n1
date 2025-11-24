"""Robust HTML parsers for MitraStar N1 pages.

This module provides parsing helpers that are resilient to small HTML variations
and can be unit-tested independently of Home Assistant.
"""
import re

MAC_RE = re.compile(r"[0-9A-Fa-f:]{17}")


def _parse_with_regex(html, regex, flags=re.DOTALL):
    if not html:
        return None
    m = re.search(regex, html, flags)
    if not m:
        return None
    return m.group(1).strip()


def _get_selected_value(html, select_name):
    if not html or not select_name:
        return None

    # 1) direct option with selected and value
    regex1 = rf'name=["\']?{re.escape(select_name)}["\']?[^>]*>.*?<option[^>]*selected[^>]*value=["\']?([^"\'>\s]+)["\']?'
    v = _parse_with_regex(html, regex1, re.DOTALL)
    if v:
        return v

    # 2) option with value then selected
    regex2 = rf'name=["\']?{re.escape(select_name)}["\']?[^>]*>.*?<option[^>]*value=["\']?([^"\'>\s]+)["\']?[^>]*selected'
    v = _parse_with_regex(html, regex2, re.DOTALL)
    if v:
        return v

    # 3) select itself carries a value attribute
    regex3 = rf'name=["\']?{re.escape(select_name)}["\']?[^>]*value=["\']?([^"\'>\s]+)["\']?'
    v = _parse_with_regex(html, regex3, re.DOTALL)
    if v:
        return v

    # 4) find select block and search inside
    regex4 = rf'name=["\']?{re.escape(select_name)}["\']?[^>]*>(.*?)</select>'
    block = _parse_with_regex(html, regex4, re.DOTALL)
    if block:
        m = re.search(r'value=["\']?([^"\'>\s]+)["\']?[^>]*selected', block)
        if m:
            return m.group(1)

    # 5) fallback: find a near-by visible text after the select
    regex5 = rf'{re.escape(select_name)}[^>]*>.*?</select>.*?</td>\s*<td[^>]*>([^<]+)</td>'
    v = _parse_with_regex(html, regex5, re.DOTALL)
    if v:
        return v

    return None


def _extract_mac(html):
    if not html:
        return None
    m = MAC_RE.search(html)
    if m:
        return m.group(0).upper()
    return None


def parse_wifi_24ghz(html):
    """Parse 2.4GHz wireless page HTML and return a dict of values."""
    if not html:
        return {}

    security_map = {'1': 'Nenhum', '2': 'WEP', '4': 'WPA2', '7': 'WPA/WPA2',
                    'psk2': 'WPA2', 'psk': 'WPA', 'open': 'Nenhum'}
    mode_map = {'1': '802.11b', '4': '802.11g', '0': '802.11b/g', '6': '802.11n', '7': '802.11g/n', '9': '802.11b/g/n'}
    bandwidth_map = {'1': 'Automático', '0': '20 MHz', '2': '40 MHz'}

    wifi_enabled = bool(re.search(r'name=["\']?WifiState["\']?[^>]*value=["\']?1["\']?[^>]*checked', html, re.DOTALL))
    ssid_broadcast = bool(re.search(r'name=["\']?broadcastSSID["\']?[^>]*checked', html, re.DOTALL))

    ssid = _parse_with_regex(html, r'name=["\']?SSID["\']?[^>]*value=["\']?([^"\']*)["\']?', re.DOTALL)
    password = _parse_with_regex(html, r'name=["\']?wlPasswd["\']?[^>]*value=["\']?([^"\']*)["\']?', re.DOTALL)

    security_code = _get_selected_value(html, 'securityMode') or _parse_with_regex(html, r'name=["\']?securityMode["\']?[^>]*>.*?<option[^>]*selected[^>]*value=["\']?([^"\'>\s]+)["\']?', re.DOTALL)
    mode_code = _get_selected_value(html, 'selectWifiMode') or _parse_with_regex(html, r'name=["\']?selectWifiMode["\']?[^>]*>.*?<option[^>]*selected[^>]*value=["\']?([^"\'>\s]+)["\']?', re.DOTALL)
    channel_code = _get_selected_value(html, 'select_Channel') or _parse_with_regex(html, r'name=["\']?select_Channel["\']?[^>]*>.*?<option[^>]*selected[^>]*value=["\']?([^"\'>\s]+)["\']?', re.DOTALL)
    bandwidth_code = _get_selected_value(html, 'select_Bandwidth') or _parse_with_regex(html, r'name=["\']?select_Bandwidth["\']?[^>]*>.*?<option[^>]*selected[^>]*value=["\']?([^"\'>\s]+)["\']?', re.DOTALL)

    wps_enabled = bool(re.search(r'name=["\']?input_wps["\']?[^>]*value=["\']?1["\']?[^>]*checked', html, re.DOTALL))
    wmm_enabled = bool(re.search(r'name=["\']?input_WMM["\']?[^>]*checked', html, re.DOTALL))

    wifi_mac = _extract_mac(html)

    frequency_band = _parse_with_regex(html, r'MLG_GVTSettings_WL_Advanced_FrBand[^>]*>[^<]*</span></td>\s*<td[^>]*>([^<]*)</td>', re.DOTALL)

    return {
        'enabled': wifi_enabled,
        'ssid': ssid,
        'ssid_broadcast': ssid_broadcast,
        'password': password if password and password != '****' else '***',
        'security': security_map.get(security_code, security_code if security_code else 'Desconhecido'),
        'wps': wps_enabled,
        'operation_mode': mode_map.get(mode_code, mode_code if mode_code else 'Desconhecido'),
        'channel': 'Automático' if channel_code in (None, '0', 0) else channel_code,
        'bandwidth': bandwidth_map.get(bandwidth_code, bandwidth_code if bandwidth_code else 'Desconhecido'),
        'mac_address': wifi_mac,
        'wmm': wmm_enabled,
        'frequency_band': frequency_band if frequency_band else '2.4 GHz',
    }


def parse_wifi_5ghz(html):
    """Parse 5GHz wireless page HTML and return a dict of values."""
    if not html:
        return {}

    security_map = {'1': 'Nenhum', '2': 'WEP', '4': 'WPA2', '7': 'WPA/WPA2', 'psk2': 'WPA2', 'psk': 'WPA', 'open': 'Nenhum'}
    mode_text_map = {'802_11n/ac': '802.11n/ac', '802_11ac': '802.11ac', '802_11n': '802.11n', '1': '802.11a', '4': '802.11ac', '6': '802.11n', '9': '802.11ac/n'}
    bandwidth_map = {'2040auto': 'Automático', '20': '20 MHz', '40': '40 MHz', '80': '80 MHz', '160': '160 MHz', '1': 'Automático', '0': '20 MHz', '2': '40 MHz', '3': '80 MHz'}

    wifi_enabled = bool(re.search(r'name=["\']?(?:WifiState5G|WifiState)["\']?[^>]*value=["\']?1["\']?[^>]*checked', html, re.DOTALL))
    ssid_broadcast = bool(re.search(r'name=["\']?(?:HideSSID|broadcastSSID5G)["\']?[^>]*checked', html, re.DOTALL))

    ssid = _parse_with_regex(html, r'name=["\']?SSID(?:5G)?["\']?[^>]*value=["\']?([^"\']*)["\']?', re.DOTALL)
    password = _parse_with_regex(html, r'name=["\']?wlPasswd(?:5G)?["\']?[^>]*value=["\']?([^"\']*)["\']?', re.DOTALL)

    security_code = _get_selected_value(html, 'securityMode_5G') or _get_selected_value(html, 'securityMode5G') or _get_selected_value(html, 'securityMode')
    mode_code_raw = _get_selected_value(html, 'select2') or _get_selected_value(html, 'selectWifiMode5G') or _get_selected_value(html, 'selectWifiMode')
    channel_code = _get_selected_value(html, 'select_Channel_5G') or _get_selected_value(html, 'select_Channel5G') or _get_selected_value(html, 'select_Channel')
    bandwidth_code = _get_selected_value(html, 'select_Bandwidth_5G') or _get_selected_value(html, 'select_Bandwidth5G') or _get_selected_value(html, 'select_Bandwidth')

    wps_enabled = bool(re.search(r'name=["\']?input_wps(?:5G)?["\']?[^>]*value=["\']?1["\']?[^>]*checked', html, re.DOTALL))
    wmm_enabled = bool(re.search(r'name=["\']?input_WMM(?:5G)?["\']?[^>]*checked', html, re.DOTALL))

    wifi_mac = _extract_mac(html)

    frequency_band = _parse_with_regex(html, r'MLG_GVTSettings_WL_Advanced_FrBand5G[^>]*>[^<]*</span></td>\s*<td[^>]*>([^<]*)</td>', re.DOTALL)

    security = security_map.get(security_code, security_code if security_code else 'Desconhecido')
    operation_mode = mode_text_map.get(mode_code_raw, mode_code_raw if mode_code_raw else 'Desconhecido')
    channel = 'Automático' if channel_code in (None, '0', 0) else channel_code
    bandwidth = bandwidth_map.get(bandwidth_code, bandwidth_code if bandwidth_code else 'Desconhecido')

    return {
        'enabled': wifi_enabled,
        'ssid': ssid,
        'ssid_broadcast': ssid_broadcast,
        'password': password if password and password != '****' else '***',
        'security': security,
        'wps': wps_enabled,
        'operation_mode': operation_mode,
        'channel': channel,
        'bandwidth': bandwidth,
        'mac_address': wifi_mac,
        'wmm': wmm_enabled,
        'frequency_band': frequency_band if frequency_band else '5 GHz',
    }
