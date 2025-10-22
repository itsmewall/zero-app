from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from ..extensions import db

class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    name = db.Column(db.String(140), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WorkflowState(db.Model):
    __tablename__ = "workflow_states"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    entity = db.Column(db.String(32), default="Task")
    name = db.Column(db.String(64), nullable=False)
    order = db.Column(db.Integer, default=0)

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    title = db.Column(db.String(200), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey("workflow_states.id"), nullable=False)
    data = db.Column(JSONB, default=dict)
    due_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
