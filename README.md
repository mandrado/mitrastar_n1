# MitraStar GPT-2741GNAC-N1 para Home Assistant

Integração customizada para Home Assistant que monitora e exibe informações do modem MitraStar GPT-2741GNAC-N1.

> Inspirado por [MitraStar_GPT-2541GNAC_HA](https://github.com/joseska/MitraStar_GPT-2541GNAC_HA). Esta é uma implementação independente específica para o modelo GPT-2741GNAC-N1.

## O que esta integração oferece

### Informações do modem
- Fabricante, modelo e versões (software/hardware)
- Números de série (geral e GPON)
- Endereços MAC (WAN/LAN)

### Wi-Fi (2.4 GHz e 5 GHz)
- Status (ativo/inativo)
- SSID e visibilidade
- Segurança (tipo de criptografia)
- Modo de operação (802.11b/g/n/ac)
- Canal e largura de banda
- Status WPS e WMM
- Endereço MAC

### Dispositivos conectados
- Lista de dispositivos DHCP ativos
- Hostname de cada dispositivo
- Endereço MAC
- Endereço IP atribuído
- Tempo de lease DHCP

## Instalação

### Via HACS (recomendado)

1. Abra o Home Assistant
2. Vá em **HACS** → **Integrations**
3. Clique nos três pontos (⋯) → **Custom repositories**
4. Cole a URL: `https://github.com/mandrado/mitrastar_n1`
5. Selecione categoria: **Integration**
6. Clique em **Add**
7. Procure por **MitraStar N1** e clique em **Install**
8. Reinicie o Home Assistant

### Manual

1. Copie a pasta `custom_components/mitrastar_n1` para o diretório `custom_components` do seu Home Assistant
2. Reinicie o Home Assistant

## Configuração

Após a instalação:

1. Vá em **Configurações** → **Dispositivos e Serviços**
2. Clique em **+ Adicionar Integração**
3. Procure por **MitraStar N1**
4. Preencha os dados solicitados:
   - **Host/IP do modem**: endereço IP do seu modem (ex.: `192.168.1.1`)
   - **Usuário**: usuário de acesso ao modem (normalmente `admin`)
   - **Senha**: senha de acesso ao modem

A integração começará a coletar dados do modem automaticamente a cada 60 segundos.

## Requisitos

- Modem MitraStar GPT-2741GNAC-N1
- Acesso à interface web do modem (IP, usuário e senha)
- Home Assistant 2023.12.0 ou superior

## Suporte

Se encontrar problemas:

1. Verifique os logs do Home Assistant (**Configurações** → **Sistema** → **Logs**)
2. Procure por erros relacionados a `mitrastar_n1`
3. Abra uma [issue no GitHub](https://github.com/mandrado/mitrastar_n1/issues) com:
   - Versão do Home Assistant
   - Logs relevantes (remova informações sensíveis)
   - Descrição do problema

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## Créditos

Inspirado pelo trabalho de [joseska/MitraStar_GPT-2541GNAC_HA](https://github.com/joseska/MitraStar_GPT-2541GNAC_HA).


