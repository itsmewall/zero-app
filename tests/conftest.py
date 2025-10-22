import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app_ctx(tmp_path):
    app = create_app()
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///:memory:", TESTING=True)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
