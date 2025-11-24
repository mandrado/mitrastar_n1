# MitraStar N1 Custom Component — Testing & Deployment Guide

## Overview

This guide provides step-by-step instructions for testing and deploying the updated MitraStar N1 Home Assistant custom component. The component now uses a dedicated `parsers.py` module with unit tests to ensure robust HTML parsing across multiple modem page variants.

## Agradecimentos / Credit

Este projeto foi idealizado a partir da ideia apresentada no repositório abaixo. A implementação deste repositório é independente e foi desenvolvida especificamente para o modelo de modem **GPT-2741GNAC-N1**; na maior parte não reutilizei código do projeto original, que foi usado apenas como inspiração técnica.

- Referência de inspiração: https://github.com/joseska/MitraStar_GPT-2541GNAC_HA

Texto curto sugerido (pode aparecer no topo do `README`):

> Este projeto foi inspirado por https://github.com/joseska/MitraStar_GPT-2541GNAC_HA. Obrigado ao autor pela ideia inicial — esta implementação é independente e direcionada ao modelo GPT-2741GNAC-N1.

Short credit (English):

> Inspired by https://github.com/joseska/MitraStar_GPT-2541GNAC_HA. Many thanks to the original author for the idea — this repository is an independent implementation tailored for the GPT-2741GNAC-N1 modem.

## File Structure

```
mitrastar_n1/                    # repository root
├── .github/ (optional CI or workflows)
├── ACKNOWLEDGEMENTS.md
├── custom_components/
│   └── mitrastar_n1/
│       ├── __init__.py
│       ├── binary_sensor.py
│       ├── config_flow.py
│       ├── const.py
│       ├── http_cgi-bin_*.htm
│       ├── manifest.json
│       ├── parsers.py
│       ├── sensor.py
│       └── tests/
│           └── test_parsers.py
├── hacs.json
├── LICENSE
└── README.md
```

Obs: mantenha os arquivos do componente dentro de `custom_components/mitrastar_n1/` quando publicar no GitHub para que HACS e o Home Assistant consigam localizar a integração.

## Instalação via HACS (passos concisos)

Pré-requisitos rápidos:
- Repositório público no GitHub contendo `custom_components/mitrastar_n1/` no root.
- `manifest.json` presente em `custom_components/mitrastar_n1/` com o campo `version` correto.
- Uma Release/Tag criada no GitHub correspondente à versão do `manifest.json` (ex.: `v1.0.0` ou `1.0.0`).

Opção A — Adicionar repositório customizado via HACS (UI):
1. Abra o Home Assistant → HACS → Integrations.
2. Clique nos três pontos (⋯) no canto superior direito → `Custom repositories`.
3. Cole a URL do seu repositório GitHub (ex.: `https://github.com/mandrado/mitrastar_n1`) e selecione a categoria `Integration`.
4. Clique em `Add`.
5. Aguarde o HACS processar; depois procure `mitrastar_n1` em HACS → Integrations e clique em `Install`.
6. Após instalar, reinicie o Home Assistant (Configurações → Sistema → Reiniciar) para ativar a integração.

Opção B — Instalação manual (sem HACS):
1. Copie a pasta `custom_components/mitrastar_n1/` para a pasta `custom_components/` da sua configuração do Home Assistant.
2. Reinicie o Home Assistant.

Comandos git úteis para preparar a publicação (local):
```powershell
cd 'C:\Users\mandr\source\repos-hacs\mitrastar_n1'
git add .
git commit -m "chore: prepare repo for HACS (manifest, LICENSE, README)"
git push origin main
# criar tag que corresponda ao "version" em manifest.json
git tag v1.0.0
git push origin --tags
```

Notas rápidas:
- Se o HACS não mostrar a integração imediatamente, clique em HACS → Integrations → three dots → `Reload` ou espere alguns minutos para o cache atualizar.
- Verifique logs do Home Assistant se a integração não aparecer ou falhar ao carregar.


## Prerequisites

- Python 3.10+ (ideally the same version as your Home Assistant OS).
- `pytest` package (for running tests locally).
- SMB network access to Home Assistant configuration folder.
- Home Assistant OS with SSH add-on available (for restart).

## Step 1: Run Unit Tests Locally (Recommended)

### Setup

Run tests from your local machine (Windows PowerShell) to validate parsers before deployment.

```powershell
# Navigate to your HA config folder (accessed via SMB or local copy)
cd "\\homeassistant.local\config"

# Create and activate a Python venv
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1

# Install dependencies
python -m pip install -U pip
python -m pip install pytest
```

If `Activate.ps1` fails due to execution policy, use the direct Python approach instead:

```powershell
# Directly invoke python from venv without activating
\\homeassistant.local\config\.venv\Scripts\python.exe -m pip install -U pip
\\homeassistant.local\config\.venv\Scripts\python.exe -m pip install pytest
```

### Run Tests

```powershell
# Option 1: Using activated venv (if activation worked)
pytest ./custom_components/mitrastar_n1/tests -q

# Option 2: Using venv python directly (if activation failed)
\\homeassistant.local\config\.venv\Scripts\python.exe -m pytest "\\homeassistant.local\config\custom_components\mitrastar_n1\tests" -q
```

**Expected Output:**
```
test_parsers.py::test_parse_wifi_24ghz PASSED
test_parsers.py::test_parse_wifi_5ghz PASSED

2 passed in 0.5s
```

If tests pass, the parsers are working correctly with your HTML samples. If they fail, check error messages and file paths are correct.

## Step 2: Deploy to Home Assistant

### Option A: Copy Files via SMB (Home Assistant OS)

Once tests pass, deploy the updated files to your Home Assistant instance.

```powershell
# Backup current __init__.py before replacing
Copy-Item -Path "\\homeassistant.local\config\custom_components\mitrastar_n1\__init__.py" `
          -Destination "\\homeassistant.local\config\custom_components\mitrastar_n1\__init__.py.bak" -Force

# Verify parsers.py exists (should already be present)
Test-Path "\\homeassistant.local\config\custom_components\mitrastar_n1\parsers.py"

# Verify test file exists
Test-Path "\\homeassistant.local\config\custom_components\mitrastar_n1\tests\test_parsers.py"
```

If `parsers.py` or `tests/test_parsers.py` are missing, they should have been created by the integration setup. If not present, copy them from your local working copy or let the system recreate them.

### Option B: Manual Verification

Before restarting Home Assistant, verify the modified files:

```powershell
# Check that __init__.py imports parsers
Select-String "from . import parsers" "\\homeassistant.local\config\custom_components\mitrastar_n1\__init__.py"

# Check that parsers.py has the parse functions
Select-String "def parse_wifi_24ghz" "\\homeassistant.local\config\custom_components\mitrastar_n1\parsers.py"
Select-String "def parse_wifi_5ghz" "\\homeassistant.local\config\custom_components\mitrastar_n1\parsers.py"
```

## Step 3: Restart Home Assistant

### Option 1: Via UI (Recommended for Home Assistant OS)

1. Open Home Assistant web UI.
2. Navigate to **Settings** → **System** → **Restart**.
3. Confirm restart.
4. Wait 2–3 minutes for Home Assistant to come back online.

### Option 2: Via SSH Add-on

If you have the SSH add-on enabled:

```bash
# Login via SSH and run
ha core restart
```

### Option 3: Power Cycle (Last Resort)

If UI/SSH are unavailable, power cycle the device.

## Step 4: Monitor and Validate

### Check Home Assistant Logs

1. Open Home Assistant web UI.
2. Navigate to **Settings** → **Devices & Services** → **Logs** (or **Developer Tools** → **Logs**).
3. Search for `mitrastar_n1` to see integration logs.
4. Look for:
   - `"Autenticação bem-sucedida com o modem."` (successful login).
   - `"Buscando about-power-box2.cgi..."` (data fetch started).
   - Any `ERROR` or `EXCEPTION` messages (check parsing issues).

### Check Entity Values

1. Navigate to **Developer Tools** → **States**.
2. Search for entities from the `mitrastar_n1` integration (e.g., `sensor.mitrastar_n1_...`).
3. Verify that WiFi 2.4GHz and 5GHz entity values are populated (not `unknown` or `Desconhecido`).
4. Check that `operation_mode`, `security`, `bandwidth`, and `mac_address` are correctly parsed.

### Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Integration fails to load | `parsers.py` missing or syntax error | Verify file exists; run `python -m py_compile parsers.py` locally to check syntax. |
| Entities show `unknown` | Parser regex didn't match HTML structure | Check modem HTML page; compare with sample files in `http_cgi-bin_*.htm`. |
| `operation_mode` is `Desconhecido` | Field name or value mapping mismatch | Check logs for warnings; may need to update mapping in `parsers.py`. |
| Login fails | Credentials or MD5 hash issue | Verify username/password in Home Assistant config; check modem login page for SID. |

## Step 5: Rollback (If Needed)

If deployment causes issues, rollback quickly:

```powershell
# Restore backup
Copy-Item -Path "\\homeassistant.local\config\custom_components\mitrastar_n1\__init__.py.bak" `
          -Destination "\\homeassistant.local\config\custom_components\mitrastar_n1\__init__.py" -Force

# Restart Home Assistant (via UI or SSH as above)
```

## Development Notes

### Adding or Updating Parsers

If the modem's HTML page changes in the future:

1. Export the new HTML view-source and save it as `http_cgi-bin_settings-wireless-network*.cgi.htm`.
2. Update the regex patterns and value mappings in `parsers.py`.
3. Run the unit tests locally:
   ```powershell
   .\\.venv\\Scripts\\python.exe -m pytest ./custom_components/mitrastar_n1/tests -v
   ```
4. Once tests pass, deploy using the steps above.

### Testing Locally Without Home Assistant

You can test parsers independently without installing Home Assistant:

```powershell
# Create a standalone test script
$parsersPath = "\\homeassistant.local\config\custom_components\mitrastar_n1\parsers.py"
$htmlPath = "\\homeassistant.local\config\custom_components\mitrastar_n1\http_cgi-bin_settings-wireless-network.cgi.htm"

# Load parsers dynamically
python -c "
import sys
sys.path.insert(0, '\\homeassistant.local\\config\\custom_components\\mitrastar_n1')
from parsers import parse_wifi_24ghz
html = open('$htmlPath').read()
result = parse_wifi_24ghz(html)
print(f'SSID: {result.get(\"ssid\")}')
print(f'Security: {result.get(\"security\")}')
print(f'MAC: {result.get(\"mac_address\")}')
"
```

## FAQ

**Q: Do I need to reinstall the component?**  
A: No. Just copy the updated files and restart Home Assistant. The component will pick up the new code automatically.

**Q: Can I roll back if something goes wrong?**  
A: Yes. Keep the `.bak` backup and restore it, then restart.

**Q: Do the HTML sample files need to stay in the component folder?**  
A: No. They're only needed for testing. You can move them to a `docs/samples/` folder if you prefer; the component won't load them at runtime.

**Q: What if my modem's HTML structure is different from the samples?**  
A: The parsers use multiple fallback patterns to handle variations. If still failing, export your modem's actual HTML page, update the sample file, and adjust regex patterns in `parsers.py`.

## Questions or Issues?

If you encounter problems:

1. Check Home Assistant logs (see **Step 4**).
2. Run unit tests locally to isolate parsing issues.
3. Compare modem HTML with sample files to spot structural differences.
4. Rollback if needed and investigate differences before redeploying.

---

**Last Updated:** November 24, 2025  
**Component Version:** mitrastar_n1 (with parsers.py)
