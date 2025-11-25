import pathlib
import importlib.util
import sys


def _load_parsers_module():
    here = pathlib.Path(__file__).parent
    module_path = (here / '..' / 'parsers.py').resolve()
    spec = importlib.util.spec_from_file_location('mitrastar_parsers', str(module_path))
    module = importlib.util.module_from_spec(spec)
    sys.modules['mitrastar_parsers'] = module
    spec.loader.exec_module(module)
    return module


def load_sample(name):
    here = pathlib.Path(__file__).parent
    p = here / 'fixtures' / f'http_cgi-bin_{name}.htm'
    return p.read_text(encoding='utf-8', errors='ignore')


def test_parse_wifi_24ghz():
    parsers = _load_parsers_module()
    html = load_sample('settings-wireless-network.cgi')
    data = parsers.parse_wifi_24ghz(html)
    assert isinstance(data, dict)
    assert data.get('ssid') is not None
    assert 'mac_address' in data
    assert data.get('operation_mode') != 'Desconhecido'


def test_parse_wifi_5ghz():
    parsers = _load_parsers_module()
    html = load_sample('settings-wireless-network-5g.cgi')
    data = parsers.parse_wifi_5ghz(html)
    assert isinstance(data, dict)
    assert data.get('ssid') is not None
    assert 'mac_address' in data
    assert data.get('operation_mode') != 'Desconhecido'
