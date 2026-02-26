# Instruções para submissão ao `home-assistant/brands`

Este arquivo contém o checklist e instruções para adicionar a sua integração `mitrastar_n1` ao repositório `home-assistant/brands`.

Resumo (o que precisa ser adicionado ao `home-assistant/brands`):

- Pasta: `custom_integrations/mitrastar_n1/`
- Arquivos (obrigatórios/fortemente recomendados):
  - `icon.png`         (obrigatório se tiver ícone)
  - `icon@2x.png`      (hDPI)
  - `logo.png`         (recomendado)
  - `logo@2x.png`      (hDPI)
  - `dark_icon.png`    (opcional, se precisar versão para tema escuro)
  # Brand images locais (Home Assistant 2026.3+)

  Com a mudança anunciada em 2026-02-24, integrações customizadas podem incluir
  as próprias imagens de marca localmente, sem PR no `home-assistant/brands`.

  Referência:
  - https://developers.home-assistant.io/blog/2026/02/24/brands-proxy-api/

  ## Estrutura esperada

  As imagens devem ficar em:

  - `custom_components/mitrastar_n1/brand/`

  Arquivos suportados:

  - `icon.png` / `dark_icon.png`
  - `logo.png` / `dark_logo.png`
  - `icon@2x.png` / `dark_icon@2x.png`
  - `logo@2x.png` / `dark_logo@2x.png`

  ## Status desta integração

  Já incluídos:

  - `custom_components/mitrastar_n1/brand/icon.png`
  - `custom_components/mitrastar_n1/brand/icon@2x.png`
  - `custom_components/mitrastar_n1/brand/logo.png`
  - `custom_components/mitrastar_n1/brand/logo@2x.png`

  ## Observações

  - As imagens locais têm prioridade sobre as imagens do CDN de brands.
  - Não é necessário configurar nada no `manifest.json` para isso funcionar.
3. Adicione a pasta `custom_integrations/mitrastar_n1/` contendo os arquivos PNG gerados.
