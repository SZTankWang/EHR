import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from EHR import db, login
from EHR import create_app

@pytest.fixture
def app():
    app = create_app("mysql+pymysql://SE:mysql@8.129.182.214:3306/test_wecare")
    yield app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            db.session.commit()
        yield client
