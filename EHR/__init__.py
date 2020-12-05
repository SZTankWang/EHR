from flask import Flask, render_template, redirect, url_for, request, json, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
import os

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 1024*1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg','.png','.pdf']
app.config["UPLOAD_FOLDER"] = "LabReport"
app.secret_key = "secretkey"
CORS(app, supports_credentials=True)
login = LoginManager(app)
login.login_view = 'login' # force user to login
login.login_message = "Please login first"

# try:
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://SE:mysql@8.129.182.214:3306/wecare"
db = SQLAlchemy(app)

from EHR.model import models

from EHR.Controller import routes_general_patient, routes_doctor_nurse