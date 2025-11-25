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
  - `dark_icon@2x.png` (opcional)
  - `dark_logo.png`    (opcional)
  - `dark_logo@2x.png` (opcional)

Regras e especificações de imagem
- Formato: PNG (transparência recomendada). Arquivos devem ser otimizados sem perda (lossless).
- Nomes: exatamente os listados acima (case-sensitive).
- Sem bordas brancas/pretas extras; as imagens devem ser cortadas (trimmed) para remover espaços vazios.

Icon (avatar-like)
- Aspect ratio: 1:1 (quadrado).
- Tamanho normal: 256×256 px (`icon.png`).
- Tamanho hDPI: 512×512 px (`icon@2x.png`).

Logo (paisagem preferida)
- Aspect ratio: respeite o logo; prefira largura maior que altura.
- Lado mais curto (shortest side):
  - Normal: >=128 px e <=256 px (`logo.png`) — por exemplo 256×96 ou 192×64.
  - hDPI: >=256 px e <=512 px (`logo@2x.png`).

Dark variants
- Se sua logo não funciona em temas escuros, forneça os arquivos com prefixo `dark_` (ex.: `dark_logo.png`). Caso não forneça, o serviço usará a variante clara como fallback.

Checklist para criar os arquivos localmente
1. Prepare o ícone quadrado (ex.: `icon.png`) em 256×256, preferencialmente com fundo transparente.
2. Gere a versão hDPI (`icon@2x.png`) em 512×512.
3. Prepare o logo (paisagem). Verifique o lado mais curto está entre 128 e 256 px.
4. Gere `logo@2x.png` com o dobro da dimensão (curto entre 256 e 512 px).
5. (Opcional) Crie versões `dark_` se necessário.
6. Otimize os PNGs (ex.: `pngcrush`, `optipng`, ou ferramentas online). Não inclua metadados desnecessários.

Estrutura do PR para `home-assistant/brands`
1. Fork o repo `home-assistant/brands`.
2. Crie um branch novo: `add/mitrastar_n1-brand`.
3. Adicione a pasta `custom_integrations/mitrastar_n1/` contendo os arquivos PNG gerados.
4. Commit e push para seu fork.
5. Abra um PR no `home-assistant/brands` com título e descrição explicando o que está adicionando (ex.: "Add MitraStar N1 brand icons (mitrastar_n1)") e inclua o `BRANDS_METADATA.json` do seu repo na descrição ou como referência.

Exemplo de mensagem do PR (copiar/colar):

Title: Add MitraStar N1 brand icons (mitrastar_n1)

Body:
```
This PR adds brand images for the custom integration `mitrastar_n1`.

Files added under `custom_integrations/mitrastar_n1/`:
- icon.png (256x256)
- icon@2x.png (512x512)
- logo.png (e.g. 256x96)
- logo@2x.png (e.g. 512x192)

Repository reference: https://github.com/mandrado/mitrastar_n1
License: MIT

Please let me know if any adjustments are required for sizes or naming.
```

Observações finais
- O processo normalmente é rápido; os mantenedores podem pedir ajuste do tamanho/crop ou naming.
- Após o merge, a imagem será servida em `https://brands.home-assistant.io/mitrastar_n1/icon.png` e `logo.png`.
