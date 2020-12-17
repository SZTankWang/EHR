import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from EHR import app as flask_app
from EHR import db, login

@pytest.fixture
def client():
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://SE:mysql@8.129.182.214:3306/test_wecare"
    with flask_app.test_client() as client:
        with flask_app.app_context():
            # db.drop_all()
            db.create_all()
            db.session.commit()
        yield client
