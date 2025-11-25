#!/usr/bin/env python3
"""Anonimiza MACs e IPs nos arquivos de teste."""
import re
from pathlib import Path

fixtures_dir = Path(__file__).parent.parent / "custom_components" / "mitrastar_n1" / "tests" / "fixtures"

# Padrões
mac_pattern = re.compile(r'[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}', re.IGNORECASE)
ip_local_pattern = re.compile(r'192\.168\.15\.(\d+)')
ip_public_patterns = [
    (r'201\.42\.55\.134', '203.0.113.100'),
    (r'200\.204\.24\.169', '203.0.113.1'),
    (r'187\.50\.250\.115', '203.0.113.115'),
    (r'187\.50\.250\.215', '203.0.113.215'),
]

# Gera MAC único baseado no original (mantém consistência)
mac_map = {}
def anonymize_mac(match):
    original = match.group(0).upper()
    if original not in mac_map:
        idx = len(mac_map) + 1
        mac_map[original] = f"AA:BB:CC:DD:{idx:02X}:{idx:02X}"
    return mac_map[original]

for htm_file in fixtures_dir.glob("*.htm"):
    print(f"Processing {htm_file.name}...")
    content = htm_file.read_text(encoding='utf-8')
    
    # Anonimiza MACs (mantendo unicidade)
    content = mac_pattern.sub(anonymize_mac, content)
    
    # Anonimiza IPs locais (192.168.15.x -> 192.168.1.x)
    content = ip_local_pattern.sub(r'192.168.1.\1', content)
    
    # Anonimiza IPs públicos
    for pattern, replacement in ip_public_patterns:
        content = re.sub(pattern, replacement, content)
    
    htm_file.write_text(content, encoding='utf-8')
    print(f"  ✓ Anonymized")

print(f"\nTotal MACs mapped: {len(mac_map)}")
