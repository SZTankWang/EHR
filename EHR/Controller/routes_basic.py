from EHR.Controller.control_helper import TIME_FORMAT, id2name
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
from EHR.model.models import *
from EHR.Controller import control_helper as helper
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
# @login_required
def nursePendingApp():
	# look up Time_slot table for next 7 days time_slot id
	next7d_slotid = helper.day2slotid(period=7)
	nurse_id = current_user.get_id()
	# nurse_id = '17711783'
	pending_app = helper.nurse_dept_appts(nurseID=nurse_id, period=7).\
									filter(
										Application.status==StatusEnum.pending,
										Application.time_slot_id.in_(next7d_slotid)).all()
	helper.load_id2name_map()
	def response_generator(app):
		return {"appID": app.id,
			"date": app.date.strftime(helper.DATE_FORMAT),
			"time": app.time.strftime(helper.TIME_FORMAT),
			"doctor": helper.id2name(app.doctor_id),
			"patient": helper.id2name(app.patient_id),
			"symptoms": app.symptoms}
	ret = [response_generator(app) for app in pending_app ]
	return make_response(jsonify(ret), 200)

@app.route('/nurseTodayAppt', methods=['GET', 'POST'])
@login_required # Otherwise, we cannot get current_user's id
def nurseTodayAppt():
	nurseID = current_user.get_id()
	# nurseID = "44116022"    # a nurseID that returns something,
	# 						for testing purpose, set the 'period' to 20
	# department ID of current nurse
	today_depts_appts = helper.nurse_dept_appts(nurseID, period=0).all()

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
	nurse_id = current_user.get_id()
	# nurseID = "17711783" # a working nurseID for testing purpose, set 'period' to 30
	# department ID of current nurse
	future_7d_appts = helper.nurse_dept_appts(nurse_id, period=7).all()

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
	nowtime = datetime.datetime.now()
	
	# testing data
	# nurse_id = '17711783'
	# nowtime = datetime.datetime.strptime("2020-11-20 13:10:00", "%Y-%m-%d %H:%M:%S")
	
	# filter1: today's appts； filter2: status=approved
	today_approved_appts = helper.nurse_dept_appts(nurseID=nurse_id, period=0).\
		filter(
			Application.status==StatusEnum.approved
			).all()

	# filter3: now() in timeslot
	now_approved_appts = []
	for appt in today_approved_appts:
		print(appt)
		appt_date_time = datetime.datetime.combine(appt.date, appt.time)
		if appt_date_time <= nowtime <= appt_date_time + timedelta(minutes=30):
			now_approved_appts.append(appt)
	
	return make_response(
		jsonify(
			[{
				"date": appt.date.strftime(helper.DATE_FORMAT),
				"time": appt.time.strftime(helper.TIME_FORMAT),
				"doctor": helper.id2name(appt.doctor_id),
				"patient": helper.id2name(appt.patient_id),
				"symptoms": appt.symptoms} for appt in now_approved_appts]
	))

@app.route('/nurseRejectedApp', methods=['GET', 'POST'])
def nurseRejectedApp():
	start_date, end_date = request.form['startDate'], request.form['endDate']
	nurse_id = current_user.get_id()
	
	# testing data
	# start_date = datetime.datetime.strptime("2020-11-20", helper.DATE_FORMAT)
	# end_date = datetime.datetime.strptime('2020-12-30', helper.DATE_FORMAT)
	# nurse_id = "17711783"

	apps = helper.nurse_dept_appts(nurseID=nurse_id, period=(end_date-start_date).days,\
		 start_date=start_date).filter(Application.status==StatusEnum.rejected)
	
	helper.load_id2name_map()
	return make_response(
		jsonify([
			{
				"appID": app.id,
				"date": app.date.strftime(helper.DATE_FORMAT),
				"time": app.time.strftime(helper.TIME_FORMAT),
				"doctor": helper.id2name(app.doctor_id),
				"patient": helper.id2name(app.patient_id),
				"symptoms": app.symptoms
			} for app in apps
		])
	)


