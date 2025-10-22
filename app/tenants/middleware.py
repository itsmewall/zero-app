from flask import g, request, current_app
from .models import Tenant

def tenant_before_request():
    header = current_app.config["TENANT_HEADER"]
    slug = request.headers.get(header)
    if not slug:
        slug = "default"
    g.tenant = Tenant.query.filter_by(slug=slug, is_active=True).first()
