import yaml
from passlib.hash import bcrypt
from .models import Tenant, User
from ..core.models import WorkflowState
from ..extensions import db

def seed_tenant(slug, blueprint_file):
    t = Tenant(slug=slug, blueprint=blueprint_file, is_active=True)
    db.session.add(t); db.session.flush()
    db.session.add(User(email=f"owner@{slug}.io", password_hash=bcrypt.hash("admin"), role="owner", tenant_id=t.id))
    data = yaml.safe_load(open(f"app/blueprints/{blueprint_file}", "r", encoding="utf8"))
    states = data["workflows"]["Task"]["states"]
    for i, name in enumerate(states):
        db.session.add(WorkflowState(tenant_id=t.id, entity="Task", name=name, order=i))
    db.session.commit()
