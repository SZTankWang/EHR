import collections
from datetime import timedelta
from itertools import count
from operator import and_, methodcaller, ne
from flask import Flask, render_template, redirect, url_for, request, json, jsonify, session, flash, make_response
from flask_login.utils import logout_user
from flask_login import login_user, logout_user, current_user, login_required
from numpy.lib.function_base import select
from werkzeug.security import check_password_hash, generate_password_hash
from EHR import app, db, login
from EHR.model.models import *
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
	if current_user.role.value == "patient":
		return render_template('patientHome.html')
	if current_user.role.value == "nurse":
		return render_template('nurseHome.html')
	if current_user.role.value == "doctor":
		pass


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
		  'n_tot_records': n_tot_records,
		  'n_tot_page': n_tot_page} for i in range(page_count)]), 200)

def page_helper(db_obj):
	try:
		curr_page = int(request.form['currPage'])
		page_size = int(request.form['pageSize'])
	except:
		curr_page = int(request.args.get('currPage'))
		page_size = int(request.args.get('pageSize'))

	n_offset = (curr_page-1) * page_size + 1
	n_tot_records = db_obj.query.count()
	n_tot_page = n_tot_records // page_size + 1
	page_count = math.ceil(n_tot_records / page_size)

	return n_offset, n_tot_records, n_tot_page, page_count


@app.route('/hospitalListPage',methods=['GET'])
def goToHospitalList():
	return render_template('hospitalListPage.html')

@app.route('/searchHospital', methods=['GET'])
def searchHospital():
	n_offset, n_tot_records, n_tot_page, page_count = page_helper(Hospital)
	partial_hpt_name = request.args.get('hospital')

	search_name = "%{}%".format(partial_hpt_name)

	rawHospitals = Hospital.query.filter(Hospital.name.like(search_name)).offset(n_offset).limit(page_count).all()


	return make_response(jsonify(
		[{"id":rawHospitals[i].id,
		  "name": rawHospitals[i].name,
		  'phone': rawHospitals[i].phone,
		  'address': rawHospitals[i].address,
		  'description': rawHospitals[i].description,
		  'n_tot_page': n_tot_page,
		  'n_tot_records': n_tot_records} for i in range(len(rawHospitals))]), 200)

@app.route('/goToHospital',methods=['GET'])
def goToHospital():
	hospitalID = request.args.get('hospitalID')
	return "success"


'''
医院列表页
返回template, 医院科室信息
'''
@app.route('/department',methods=['GET'])
def department():
	return render_template('patientDepartment.html')

@app.route('/nurseHome', methods=['GET'])
def nurseHome():
	return render_template('nurseHome_save.html')
	# return redirect(url_for('pendingApp'))

@app.route('/pendingApp', methods=['GET', 'POST'])
def pendingApp():
	pending_app = Application.query.filter(and_(Application.app_timestamp>=datetime.datetime.now(),
												Application.status==StatusEnum.pending)).limit(6).all()
	return make_response(jsonify(
				[{"appID": pending_app[i].id,
				"date": pending_app[i].app_timestamp.strftime("%Y-%m-%d"),
				"time": pending_app[i].app_timestamp.strftime("%H:%M"),
				"doctor": pending_app[i].doctor_id,
				"patient": pending_app[i].patient_id,
				"symptoms": pending_app[i].symptoms} for i in range(len(pending_app))]), 200)

@app.route('/todayAppt', methods=['GET', 'POST'])
def todayAppt():
	userID = current_user.id
	# dept. of current nurse
	deptID = Nurse.query.filter_by(userID=Nurse.id).with_entities('department_id')
	print(deptID)

	# today_appt_list = Application.query.

@app.route('/viewAppt', methods=['POST'])
def viewAppt():
	appid = request.form['appID']

@app.route('/availSlot', methods=['POST', 'GET'])
def availSlot():
	# doctorID = request.args.get('doctorID')
	doctorID = '46768069'
	today = datetime.date.today()
	avail_7d_slots = Time_slot.query.filter(
					# future 7 days
					Time_slot.slot_date>=today,
					Time_slot.slot_date<=today+timedelta(days=100),
					Time_slot.doctor_id==doctorID,
					Time_slot.n_total>Time_slot.n_booked
	).order_by(Time_slot.slot_date).all()
	avail_slots_list =[{'date': v.slot_date,
				'time_seg_id': v.slot_seg_id,
				'n_left_slot': v.n_total-v.n_booked} for v in avail_7d_slots]

	counter=0
	daily_AMPM_slots = collections.defaultdict(int)
	response = []
	cur_day = today

	for d in range(7):
		cur_day = today + timedelta(days=d)
		cur_res = {'date': cur_day, 'morning':0, 'afternoon': 0}
		while counter<len(avail_slots_list) and avail_slots_list[counter]['date'] == cur_day:
			short = avail_slots_list[counter]
			cur_res['morning'] += 1 if short['time_seg_id']<=3 else 0
			cur_res['afternoon'] += 1 if short['time_seg_id']>3 else 0
			counter += 1

		response.append(cur_res)
	return make_response(
		jsonify(response),200
	)
