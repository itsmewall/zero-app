from flask_smorest import Blueprint
from flask import request, g
from .models import Task, WorkflowState
from ..extensions import db

blp = Blueprint("core", __name__, description="Core")

@blp.route("/tasks", methods=["GET"])
def list_tasks():
    qs = Task.query.filter_by(tenant_id=g.tenant.id).all()
    return [{"id":t.id,"title":t.title,"state_id":t.state_id,"data":t.data} for t in qs]

@blp.route("/tasks", methods=["POST"])
def create_task():
    p = request.get_json() or {}
    st = WorkflowState.query.filter_by(tenant_id=g.tenant.id, id=p["state_id"]).first()
    t = Task(tenant_id=g.tenant.id, title=p["title"], state_id=st.id, data=p.get("data",{}))
    db.session.add(t); db.session.commit()
    return {"id":t.id}, 201
