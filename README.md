# App Zero Flask
Template multi-tenant em Flask para gestão de atividades com blueprint declarativo e dashboards plugáveis.

## Rodar local
python -m venv .venv
. .venv/Scripts/activate  # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
flask db init && flask db migrate -m "init" && flask db upgrade
python -c "from app import create_app; from app.extensions import db; from app.tenants.seed import seed_tenant; app=create_app(); app.app_context().push(); seed_tenant('default','restaurant.yaml')"
flask run -p 8000

## Docker
cd deploy
docker compose up -d --build
