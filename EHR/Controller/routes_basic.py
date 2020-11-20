from EHR.Controller.control_helper import DATE_FORMAT, TIME_FORMAT, id2name, slot2time
import collections
from datetime import timedelta
from itertools import count
from flask import Flask, render_template, redirect, url_for, request, json, jsonify, session, flash, make_response
from flask.signals import appcontext_tearing_down
from flask_login.utils import logout_user
from flask_login import login_user, logout_user, current_user, login_required
from numpy.lib.function_base import select
from sqlalchemy.util.langhelpers import methods_equivalent
from werkzeug.security import check_password_hash, generate_password_hash
from EHR import app, db, login
from EHR.model.models import *
from EHR.Controller import control_helper as helper
import math
import datetime
from time import strftime, time


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
		return make_response(jsonify({'ret':1,'message':'You already registered!'}))
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
		helper.load_id2name_map()
		return make_response(jsonify({"ret":0, 'message':""}), 200)
	except:
		db.session.rollback()
		return make_response(jsonify({'ret':1, 'message':"error"}))


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
				# update roster
				helper.load_id2name_map()
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

	n_offset, n_tot_records, n_tot_page, page_count = helper.paginate(Hospital)

	rawHospitals = Hospital.query.offset(n_offset).limit(page_count).all()

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
		  'n_tot_page': n_tot_page} for i in range(len(rawHospitals))]), 200)


@app.route('/hospitalListPage',methods=['GET'])
def goToHospitalList():
	return render_template('hospitalListPage.html')

@app.route('/searchHospital', methods=['GET'])
def searchHospital():
	n_offset, n_tot_records, n_tot_page, page_count = helper.paginate(Hospital)
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
	# hospitalID = request.args.get('hospitalID')
	# departments = Hospital.query.filter
	pass
'''
医院列表页
返回template, 医院科室信息
'''
@app.route('/department',methods=['GET'])
def department():
	return render_template('patientDepartment.html')

@app.route('/nurseTodayAppt', methods=['GET', 'POST'])
@login_required
def todayAppt():
	nurseID = current_user.get_id()
	# applications for the same department where this.nurse is working for

	same_dept_appts = helper.nurse_dept_appts(nurseID=nurseID, period=0).all()

	def response_generator(i):
		slot_id = same_dept_appts[i].time_slot_id
		slot_date, seg_start_t = helper.slot2time(slot_id)
		return {"appID": same_dept_appts[i].id,
			"date": slot_date.strftime("%Y-%m-%d"),
			"time": seg_start_t.strftime("%H:%M"),
			"doctor": helper.id2name(same_dept_appts[i].doctor_id),
			"patient": helper.id2name(same_dept_appts[i].patient_id),
			"symptoms": same_dept_appts[i].symptoms}

	return make_response(jsonify(
				[response_generator(i) for i in range(len(pending_app)) ]), 200)

@app.route('/nurseTodayAppt', methods=['GET', 'POST'])
@login_required
def todayAppt():
	# userID = current_user.get_id()
	userID = "33107734"
	# department ID of current nurse
	deptID = Nurse.query.filter(Nurse.id==userID).first().department_id
	# applications for the same department where this.nurse is working for
	same_dept_appts = Application.query.\
					join(Nurse, Nurse.id==Application.approver_id).\
						filter(Nurse.department_id==deptID).all()

	def response_generator(i):
		slot_id = same_dept_appts[i].time_slot_id
		slot_date, seg_start_t = helper.slot2time(slot_id)
		return {"appID": same_dept_appts[i].id,
			"date": slot_date.strftime("%Y-%m-%d"),
			"time": seg_start_t.strftime("%H:%M"),
			"doctor": helper.id2name(same_dept_appts[i].doctor_id),
			"patient": helper.id2name(same_dept_appts[i].patient_id),
			"symptoms": same_dept_appts[i].symptoms}

	return make_response(jsonify(
				[response_generator(i) for i in range(len(same_dept_appts)) ]), 200)

@app.route('/nurseTodayAppt', methods=['GET', 'POST'])
@login_required
def todayAppt():
	# userID = current_user.get_id()
	userID = "33107734"
	# department ID of current nurse
	deptID = Nurse.query.filter(Nurse.id==userID).first().department_id
	# applications for the same department where this.nurse is working for
	same_dept_appts = Application.query.\
					join(Nurse, Nurse.id==Application.approver_id).\
						filter(Nurse.department_id==deptID).all()

	def response_generator(i):
		slot_id = same_dept_appts[i].time_slot_id
		slot_date, seg_start_t = helper.slot2time(slot_id)
		return {"appID": same_dept_appts[i].id,
			"date": slot_date.strftime("%Y-%m-%d"),
			"time": seg_start_t.strftime("%H:%M"),
			"doctor": helper.id2name(same_dept_appts[i].doctor_id),
			"patient": helper.id2name(same_dept_appts[i].patient_id),
			"symptoms": same_dept_appts[i].symptoms}

	return make_response(jsonify(
				[response_generator(i) for i in range(len(same_dept_appts)) ]), 200)


	# today_appt_list = Application.query.

@app.route('/doctorAvailSlot', methods=['POST', 'GET'])
def doctorAvailSlot():
	doctorID = request.args.get('doctorID')
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


#---------------------------nurse--------------------------------
#---------------------------nurse--------------------------------
#---------------------------nurse--------------------------------
# page 1
@app.route('/nurseHome', methods=['GET', 'POST'])
@login_required
def nurseHome():
	return render_template('nurseHome.html')
# page 2
@app.route('/nurseAllAppt', methods=['GET', 'POST'])
@login_required
def nurseAllAppt():
	return render_template('nurseAllAppt.html')

'''
page 1: nurseHome
routes: nursePendingApp, nurseTodayAppt
'''
@app.route('/nursePendingApp', methods=['GET', 'POST'])
@login_required
def nursePendingApp():
	# look up Time_slot table for next 7 days time_slot id
	next7d_slotid = helper.day2slotid(period=100)
	nurseID = current_user.get_id()
	pending_app = helper.nurse_dept_appts(nurseID=nurseID, period=100).\
									filter(
										Application.status==StatusEnum.pending,
										Application.time_slot_id.in_(next7d_slotid)).all()
	helper.load_id2name_map()
	def response_generator(i):
		slot_id = pending_app[i].time_slot_id
		slot_date, seg_start_t = helper.slot2time(slot_id)
		return {"appID": pending_app[i].id,
			"date": slot_date.strftime("%Y-%m-%d"),
			"time": seg_start_t.strftime("%H:%M"),
			"doctor": helper.id2name(pending_app[i].doctor_id),
			"patient": helper.id2name(pending_app[i].patient_id),
			"symptoms": pending_app[i].symptoms}
	ret = [response_generator(i) for i in range(len(pending_app)) ]
	return make_response(jsonify(ret), 200)

@app.route('/nurseTodayAppt', methods=['GET', 'POST'])
@login_required # Otherwise, we cannot get current_user's id
def nurseTodayAppt():
	nurseID = current_user.get_id()
	# nurseID = "44116022"    # a nurseID that returns something,
	# 						for testing purpose, set the 'period' to 20
	# department ID of current nurse
	today_depts_appts = helper.nurse_dept_appts(nurseID, period=100).all()

	helper.load_id2name_map()
	def response_generator(i):
		slot_id = today_depts_appts[i].time_slot_id
		slot_date, seg_start_t = helper.slot2time(slot_id)
		return {"appID": today_depts_appts[i].id,
			"date": slot_date.strftime("%Y-%m-%d"),
			"time": seg_start_t.strftime("%H:%M"),
			"doctor": helper.id2name(today_depts_appts[i].doctor_id),
			"patient": helper.id2name(today_depts_appts[i].patient_id),
			"symptoms": today_depts_appts[i].symptoms}

	return make_response(jsonify(
				[response_generator(i) for i in range(len(today_depts_appts)) ]), 200)

@app.route('/nurseFutureAppt', methods=['GET'])
@login_required
def nurseFutureAppt():
	nurseID = current_user.get_id()
	# nurseID = "46770556" # a working nurseID for testing purpose, set 'period' to 30
	# department ID of current nurse
	future_7d_appts = helper.nurse_dept_appts(nurseID, period=100).all()

	helper.load_id2name_map()
	helper.load_slots()
	def response_generator(i):
		slot_id = future_7d_appts[i].time_slot_id
		slot_date, seg_start_t = helper.slot2time(slot_id)
		return {"appID": future_7d_appts[i].id,
			"date": slot_date.strftime("%Y-%m-%dR"),
			"time": seg_start_t.strftime("%H:%M"),
			"doctor": helper.id2name(future_7d_appts[i].doctor_id),
			"patient": helper.id2name(future_7d_appts[i].patient_id),
			"symptoms": future_7d_appts[i].symptoms}
	return make_response(jsonify(
				[response_generator(i) for i in range(len(future_7d_appts)) ]), 200)

# @app.route('nurseProcessApp')

# page 3 Create Appt
@app.route('/nurseGoCreateAppt', methods=['GET', 'POST'])
@login_required
def nurseGoCreateAppt():
	return render_template('nurseCreateAppt.html')


# page 4 View Appt
@app.route('/nurseGoViewAppt/<string:appID>', methods=['GET', 'POST'])
@login_required
def nurseGoViewAppt(appID):
	appt_res = Application.query.filter(Application.id==appID).first()
	slot_date, seg_start_t = helper.slot2time(appt_res.time_slot_id)

	helper.load_id2name_map()
	return render_template('nurseViewAppt.html',
		appID=appID,
		date=slot_date.strftime(helper.DATE_FORMAT),
		time=seg_start_t.strftime(helper.TIME_FORMAT),
		doctor=helper.id2name(appt_res.doctor_id),
		patientID=appt_res.patient_id,
		patient=helper.id2name(appt_res.patient_id),
		symptoms=appt_res.symptoms,
		comments=appt_res.reject_reason,
		mcID=None,
		appStatus=appt_res.status)

@app.route('/nurseViewAppt', methods=['GET','POST'])
@login_required
def nurseviewAppt():

	mcid = request.form['mcID']
	mc = Medical_record.query.filter(Medical_record.id==mcid).first()


# 	preExam: {
# bodyTemperature: float/str,
# pulseRate: float/str,
# bloodPressure: float/str}

# diagnosis:str

# prescriptions: [{medicine, comments, etc.}, {}, ...]

# labReportTypes:[{id:str, name:str}, {}, ...]

# }

	return make_response(
		jsonify(
			{"bodyTemperature": mc.body_temperatur,
			"pulseRate": mc.heart_rate.strftime("%Y-%m-%d")}
			# "time": seg_start_t.strftime("%H:%M"),
			# "doctor": helper.id2name(appt_res.doctor_id),
			# "patient": helper.id2name(appt_res.patient_id),
			# "symptoms": appt_res.symptoms,
			# "comments": appt_res.reject_reason}
		)
	)

@app.route('/nurseUploadLabReport', methods=['GET', 'POST'])
@login_required
def nurseUploadLabReport():
	mcID = request.form['mcID']
	typeID = request.form['typeID']
	labReport = request.files['labReport']
	comments = request.form['comments']
	#TODO
	return make_response(jsonify({"ret": 0}))

@app.route('/nurseProcessApp', methods=['GET','POST'])
def nurseProcessApp():
	appID = request.form['appID']
	# get Appt
	appt = Application.query.filter(Application.id==appID).first()
	if not appt:
		return {'ret': f'The appointment: {appID} does not exists!'}

	decision = request.form['action']
	if decision.lower() == 'reject':
		appt.status = StatusEnum.rejected
		appt.reject_reason = request.form['comments']
	elif decision.lower() == 'approve':
		appt.status = StatusEnum.approved

	db.session.commit()

	return make_response({'ret':0})

@app.route('/nurseOnGoingAppt', methods=['GET'])
def nurseOnGoingAppt():
	helper.load_id2name_map() # save this, only for development use
	nurse_id = current_user.get_id()
	# nurse_id = '46770556'
	today_appts = helper.nurse_dept_appts(nurseID=nurse_id, period=0).all()
	on_going_appts = {}
	nowtime = datetime.datetime.now()
	# nowtime = datetime.datetime.strptime("2020-11-19 09:05:00", "%Y-%m-%d %H:%M:%S")

	for appt in today_appts:
		appt_date, appt_start_time = helper.slot2time(appt.time_slot_id)
		appt_date_time = datetime.datetime.combine(appt_date, appt_start_time)
		print(appt)
		if appt_date_time <= nowtime <= appt_date_time + timedelta(minutes=30):
			on_going_appts[appt.id] = (appt, appt_date, appt_start_time)

	return make_response(
		jsonify(
			[{
				"date": on_going_appts[apptid][1].strftime("%Y-%m-%d"),
				"time": on_going_appts[apptid][2].strftime("%H:%M"),
				"doctor": helper.id2name(on_going_appts[apptid][0].doctor_id),
				"patient": helper.id2name(on_going_appts[apptid][0].patient_id),
				"symptoms": on_going_appts[apptid][0].symptoms} for apptid in on_going_appts.keys()]
	))

@app.route('/nurseRejectedApp', methods=['GET','POST'])
def nurseRejectedApp():
	"""
	get the 'rejcted' appt within the startdate, enddate
	"""
	# app_start_date = request.form['startDate']
	# app_end_date = request.form['endDate']
	app_start_date = datetime.datetime.strptime("2020-12-01", helper.DATE_FORMAT)
	app_end_date = datetime.datetime.strptime('2020-12-30', helper.DATE_FORMAT)

	slot_ids = helper.day2slotid(period=(app_end_date-app_start_date).days, start_day=app_start_date)
	nurseID = current_user.get_id()
	appts = helper.nurse_dept_appts(nurseID=nurseID,
									period=app_end_date-app_start_date,
									start_date=app_start_date)\
										.filter(
											Application.id.in_(slot_ids),
											Application.status==StatusEnum.rejected
											).all()
	# for test purpose
	helper.load_slots()
	helper.load_id2name_map()

	return make_response(
		jsonify(
			[{
				"appID": app.id,
				"date": helper.slot2time(app.time_slot_id)[0].strftime(helper.DATE_FORMAT),
				"time": helper.slot2time(app.time_slot_id)[1].strftime(helper.TIME_FORMAT),
				"doctor": helper.id2name(app.doctor_id),
				"patient": helper.id2name(app.patient_id),
				"symptoms": app.symptoms,
				"status": app.status
			}for app in appts]
		)
	)

@app.route('/nurseGoViewMC', methods=['GET','POST'])
def nurseGoViewMC():
	#TODO
	return render_template("nurseViewMC.html")

@app.route('/nurseViewMC', methods=['GET','POST'])
def nurseViewMC():
	#TODO
	return make_response(jsonify([{"appID":"1", "mcID":"1", "date":"1", "time":"1", "doctor":"1", "symptoms":"1"}]))

@app.route('/nurseGetComments', methods=['GET','POST'])
def nurseGetComments():
	#TODO
	return make_response(jsonify({"comments":"1"}))
