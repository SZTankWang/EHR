from operator import and_, methodcaller, ne
from flask import Flask, render_template, redirect, url_for, request, json, jsonify, session, flash, make_response
from flask_login.utils import logout_user
from flask_login import login_user, logout_user, current_user, login_required
from numpy.lib.function_base import select
from werkzeug.security import check_password_hash, generate_password_hash
from myApp import app, db, login
from myApp.model.models import *
import math
import datetime


@app.route('/')
def home():
	if current_user.is_authenticated:
		return redirect(url_for('loadHomePage'))
	return render_template('index.html')

#-------------------Register--------------------
#-------------------Register--------------------

@app.route('/register', methods=['POST'])
def register():
	"""
		patient: register by (national)id
		doctor/nurse: register by (license)id
	"""
	if current_user.is_authenticated:
		return redirect(url_for('loadHomePage'))
	id = request.form['id']
	print(User.query.filter_by(id=id).first() != None)
	if User.query.filter_by(id=id).first() != None:
		return make_response(jsonify({'ret': 'You already registered!'}))
	role = request.form['role']
	first_name = request.form['firstName']
	last_name = request.form['lastName']

	phone = request.form['phone']
	email = request.form['email']
	password = request.form['password']
	if role != "patient":
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
		return make_response(jsonify({"ret":0}), 200)
	except:
		db.session.rollback()
		return make_response(jsonify({'ret':"error"}))


#--------------------Login---------------------
#--------------------Login---------------------

@app.route('/login', methods=['GET','POST'])
def login():
	"""
		patient login with: national id + password
		doctor/patient login with: license id + password
	"""
	if request.method == 'GET':
		if current_user.is_authenticated:
			return redirect(url_for('loadHomePage'))
		return render_template('login.html')
	if request.method == 'POST':
		if not current_user.is_authenticated:
			id = request.form['id']
			password = request.form['password']

			try:
				user = User.query.get(id)
				if not user:
					# flash("Unregistered ID or wrong password")
					return make_response(jsonify({"ret": "Unregistered user"}))
				if not user.check_password(password):
					return make_response(jsonify({"ret": "Incorrect password"}))
				login_user(user)
			except:
				# flash("Unknown error, sorry!")
				return make_response(jsonify({"ret": "Unknown error"}))
		return make_response(jsonify({"ret":0, "role":current_user.role.value, "id": current_user.id}))
		#redirect(url_for(f'{current_user.role.value}Home'))

#--------------------Logout---------------------
#--------------------Logout---------------------

@app.route('/logout', methods=['GET'])
def logout():
	logout_user()
	return redirect(url_for('home'))


#--------------------home---------------------
#--------------------home---------------------
@app.route('/loadHomePage', methods=['GET'])
@login_required
def loadHomePage():
	# return render_template(f'{current_user.role.value}Home.html')
	return render_template('patientHome.html')


#--------------------get hospital list data---------------------
#--------------------get hospital list data---------------------

@app.route('/hospitalData', methods=['GET','POST'])
def hospitalData():
	# try:
	if request.method == "GET":
		return redirect(url_for('goToHospitalList'))
	# curr_page = int(request.form['currPage'])
	# page_size = int(request.form['pageSize'])

	n_offset, n_tot_records, n_tot_page, page_count = page_helper(Hospital)

	rawHospitals = Hospital.query.offset(n_offset).limit(page_count)
	print(rawHospitals)
	hospital_ids = [res.id for res in rawHospitals]
	hospital_names = [res.name for res in rawHospitals]
	hospital_addresses = [res.address for res in rawHospitals]
	hospital_phones = [res.phone for res in rawHospitals]
	# return data
	return make_response(jsonify(
		[{"id":hospital_ids[i],
		  "name": hospital_names[i],
		  "address": hospital_addresses[i],
		  "phone": hospital_phones[i],
		  'n_tot_record': n_tot_records,
		  'n_tot_page': n_tot_page} for i in range(page_count)]), 200)

def page_helper(db_obj):
	curr_page = int(request.form['currPage'])
	page_size = int(request.form['pageSize'])

	n_offset = (curr_page-1) * page_size + 1
	n_tot_records = db_obj.query.count()
	n_tot_page = n_tot_records // page_size + 1
	page_count = math.ceil(n_tot_records / page_size)

	return n_offset, n_tot_records, n_tot_page, page_count


@app.route('/hospitalListPage',methods=['GET'])
def goToHospitalList():
	return render_template('hospitalListPage.html')

@app.route('/searchHostpital', methods=['GET'])
def searchHospital():

	n_offset, n_tot_records, n_tot_page, page_count = page_helper(Hospital)
	rawHospitals = Hospital.query.offset(n_offset).limit(page_count)
	hospital_ids = [res.id for res in rawHospitals]
	hospital_names = [res.name for res in rawHospitals]
	# return data
	return make_response(jsonify(
		[{"id":hospital_ids[i],
		  "name": hospital_names[i],
		  'n_tot_record': n_tot_records,
		  'n_tot_page': n_tot_page} for i in range(page_count)]), 200)

@app.route('/nurseHome', methods=['GET'])
def nurseHome():
	return render_template('nurseHome_save.html')
	# return redirect(url_for('pendingApp'))

@app.route('/pendingApp', methods=['GET', 'POST'])
def pendingApp():
	if request.method == 'POST':
		print("Here to get data")
		pending_appt = Application.query.filter(and_(Application.app_timestamp>=datetime.datetime.now(),
													Application.status==StatusEnum.pending)).limit(6).all()
		return make_response(jsonify(
					[{"appID": pending_appt[i].id,
					"date": pending_appt[i].app_timestamp,
					"doctor": pending_appt[i].doctor_id,
					"patient": pending_appt[i].patient_id,
					"symptoms": pending_appt[i].symptoms} for i in range(len(pending_appt))]), 200)

@app.route('/todayAppt', methods=['GET', 'POST'])
def todayAppt():
	# unclear question. Do you wanna check "my dept." appt?
	pass

# @app.route('/viewAppt', methods=['POST'])
# def viewAppt():
# 	appid = request.form['appID']
	
