from EHR.Controller.control_helper import DATE_FORMAT, TIME_FORMAT, id2name
import collections
from datetime import timedelta
from itertools import count
from time import strftime
from flask import Flask, render_template, redirect, url_for, request, json, jsonify, session, flash, make_response
from flask.signals import appcontext_tearing_down
from flask_login.utils import logout_user
from flask_login import login_user, logout_user, current_user, login_required
from numpy.core.arrayprint import TimedeltaFormat
from numpy.lib.function_base import select
from sqlalchemy.util.langhelpers import methods_equivalent
from werkzeug.security import check_password_hash, generate_password_hash
from EHR import app, db, login
#from flask import current_app as app
from EHR.model.models import *
from EHR.Controller import control_helper as helper
import datetime


#-------------------General--------------------
#-------------------General--------------------
#-------------------General--------------------
#---public page---
@app.route('/')
def home():
	if current_user.is_authenticated:
		return redirect(url_for('loadHomePage'))
	return render_template('index.html')


#---register---
@app.route('/register', methods=['GET', 'POST'])
def register():
	"""
		patient: register by (national)id
		doctor/nurse: register by (license)id
	"""
	if current_user.is_authenticated:
		return redirect(url_for('loadHomePage'))
	id = request.form['id']

	if User.query.filter_by(id=id).first() != None:
		return make_response(jsonify({'ret':1,'message':'You already registered!'}))
	role = request.form['role']
	first_name = request.form['firstName']
	last_name = request.form['lastName']

	phone = request.form['phone']
	email = request.form['email']
	password = request.form['password']
	if role == "nurse" or role == "doctor":
		department = request.form['department']

	user = User(id=id, first_name=first_name, last_name=last_name,
				role=role, email=email, phone=phone, password_hash=generate_password_hash(password))
	try:
		db.session.add(user)
		# update corresponding table
		if role == "patient":
			patient = Patient(id=id)
			db.session.add(patient)
		elif role == "doctor":
			doctor = Doctor(id=id, department_id = department)
			db.session.add(doctor)
		elif role == "nurse":
			nurse = Nurse(id=id, department_id = department)
			db.session.add(nurse)
		db.session.commit()

		helper.load_id2name_map(True)
		return make_response(jsonify({"ret":0, 'message':""}), 200)
	except:
		db.session.rollback()
		return make_response(jsonify({'ret':1, 'message':"error"}))


#---login---
@app.route('/login', methods=['GET','POST'])
def login():
	"""
		patient login with: national id + password
		doctor/patient login with: license id + password
	"""
	if request.method == 'GET':
		if current_user.is_authenticated:
			helper.load_id2name_map(True)
			return redirect(url_for('loadHomePage'))
		return render_template('login.html')
	if request.method == 'POST':
		if not current_user.is_authenticated:
			id = request.form['id']
			password = request.form['password']
			try:
				user = User.query.get(id)
				if not user:
					return make_response(jsonify({"ret":1, "message": "Unregistered user"}))
				if not user.check_password(password):
					return make_response(jsonify({"ret":1, "message": "Incorrect password"}))
				login_user(user)
				# update roster
				helper.load_id2name_map(True)
			except:
				# flash("Unknown error, sorry!")
				return make_response(jsonify({"ret":1, "message": "Unknown error"}))
		return make_response(jsonify({"ret":0, "role":current_user.role.value, "id": current_user.id}))


#---logout---
@app.route('/logout', methods=['GET'])
def logout():
	logout_user()
	return redirect(url_for('home'))


#---go to home---
@app.route('/loadHomePage', methods=['GET'])
@login_required
def loadHomePage():
	# return render_template(f'{current_user.role.value}Home.html')
	if current_user.role.value == "patient":
		return render_template('patientHome.html')
	if current_user.role.value == "nurse":
		return render_template('nurseHome.html')
	if current_user.role.value == "doctor":
		return render_template('doctorHome.html')
	if current_user.role.value == "admin":
		return render_template('admin.html')


#---go to home---
@app.route('/loadAllAppt', methods=['GET'])
@login_required
def loadAllAppt():
	# return render_template(f'{current_user.role.value}Home.html')
	if current_user.role.value == "patient":
		return render_template('patientHome.html')
	if current_user.role.value == "nurse":
		return render_template('nurseAllAppt.html')
	if current_user.role.value == "doctor":
		return render_template('doctorAllAppt.html')
