# KM Solidario Caminhos de Rosa

Protótipo Django para campanha de venda simbólica dos 160 km da prova.

## Como rodar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py ensure_admin
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`.

## Fluxo de validação manual

1. A pessoa escolhe um ou mais KMs disponíveis.
2. Ela preenche os dados, informa o valor e envia o comprovante do PIX.
3. O KM fica como "Aguardando conferência do PIX".
4. Você entra em `/painel/`, a Caderneta da Travessia, seleciona os KMs e clica em "Dar como certo".
5. Se o PIX não for válido, use "Soltar de novo".

## Ajustes iniciais

- Troque `PIX_KEY` no arquivo `.env`.
- Troque `SUGGESTED_KM_VALUE` no arquivo `.env` (mínimo atual: R$ 30).
- A senha da Caderneta vem do `.env`: `ADMIN_PASSWORD=BOIZAO`.
- Quando tiver a logo oficial, substitua o monograma `CR` no template base por uma imagem em `static/campaign/img/`.

## Deploy no Render

No Web Service do Render, configure:

```text
Build Command: bash build.sh
Start Command: gunicorn caminhos_rosa.wsgi:application
```

Variáveis de ambiente principais:

```text
DATABASE_URL=<Internal Database URL do Postgres>
DJANGO_SECRET_KEY=<uma chave forte>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<seu-app>.onrender.com
ADMIN_PASSWORD=<senha da Caderneta>
PIX_KEY=mtb199701@gmail.com
PIX_COPY_PASTE=<codigo pix copia e cola>
SUGGESTED_KM_VALUE=30
WHATSAPP_NUMBER=5531988759513
```
