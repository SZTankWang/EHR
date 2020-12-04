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
		helper.load_id2name_map()
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
					return make_response(jsonify({"ret":1, "message": "Unregistered user"}))
				if not user.check_password(password):
					return make_response(jsonify({"ret":1, "message": "Incorrect password"}))
				login_user(user)
				# update roster
				helper.load_id2name_map()
			except:
				# flash("Unknown error, sorry!")
				return make_response(jsonify({"ret":1, "message": "Unknown error"}))
		return make_response(jsonify({"ret":0, "role":current_user.role.value, "id": current_user.id}))
		#redirect(url_for(f'{current_user.role.value}Home'))


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



#--------------------Patient---------------------
#--------------------Patient---------------------
#--------------------Patient---------------------

#---get hospital list data---
@app.route('/hospitalData', methods=['GET','POST'])
def hospitalData():
	# try:
	if request.method == "GET":
		return redirect(url_for('goToHospitalList'))
	# curr_page = int(request.form['currPage'])
	# page_size = int(request.form['pageSize'])

	n_offset, n_tot_records, n_tot_page, page_count = helper.paginate(Hospital)

	rawHospitals = Hospital.query.offset(n_offset-1).limit(page_count).all()

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
	partial_hpt_name = request.args.get('searchKey')
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

@app.route('/goToHospital/<hospitalID>',methods=['GET'])
@login_required
def goToHospital(hospitalID):
	department_ID,department_name = helper.hosp2dept(hospitalID)
	return render_template("patientDepartment.html",hospital_ID=hospitalID,
	department_list=[{'departmentID':department_ID[i],
	'departmentName':department_name[i]} for i in range(len(department_ID))])

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

@app.route('/getDoctorByDept', methods=['GET', 'POST'])
@login_required
def getDoctorByDept():
	deptID = request.args.get('deptID')
	return make_response(jsonify(helper.dept2doc_all(deptID)))

'''
	返回医生页面
	参数：doctorID
	返回：render_template(页面，信息)
'''
@app.route('/viewDoctor/<doctorID>',methods=['GET'])
def viewDoctorByID(doctorID):
	doctor = Doctor.query.join(Department, Doctor.department_id == Department.id).\
					join(Hospital,Department.hospital_id == Hospital.id).filter(Doctor.id == doctorID).first()
	helper.load_id2name_map()
	doctorName = id2name(doctorID)
	hospital = doctor.department.hospital.name
	department = doctor.department.title
	return render_template('doctorPage.html',
						doctorID = doctorID,
						doctorName = doctorName,
						hospital = hospital,
						department = department)


@app.route('/getDoctorSlot',methods=['GET','POST'])
@login_required
def getDoctorSlot():
	doctorID = request.args.get('doctorID')
	date = request.args.get('date')
	date = datetime.datetime.strptime(date,'%Y-%m-%d')
	slot_list = helper.doc2slots_available(doctorID, 0, start_date=date)
	avail_num_list = [(slot_list[i].n_total-slot_list[i].n_booked) for i in range(len(slot_list))]
	date_list = [helper.t_slotid2date(slot_list[i].id) for i in range(len(slot_list))]
	time_list = [helper.t_slot2time(slot_list[i].id) for i in range(len(slot_list))]
	return make_response(
		jsonify(
			[{"slotID": str(slot_list[i].id),
			"avail_num":str(avail_num_list[i]),
			"slotTime": datetime.datetime.combine(date_list[i],time_list[i]).strftime("%Y-%m-%d %H:%M")}
			 for i in range(len(slot_list))]),200)


@app.route('/querySlotInfo',methods=['GET'])
@login_required
def querySlotInfo():
	slotID = request.args.get('slotID')
	return make_response(
		jsonify({"slotTime": datetime.datetime.combine(helper.t_slotid2date(slotID),helper.t_slot2time(slotID)).strftime("%Y-%m-%d %H:%M")})
		)

@app.route('/makeAppt',methods=['GET','POST'])
@login_required
def makeAppt():
	try:
		patient_id = current_user.get_id()
		symptom = request.form['symptom']
		time_slot_id = request.form['slotID']
		doctor_id = request.form['doctorID']
		slot = Time_slot.query.filter(Time_slot.id == time_slot_id).first()
		#doctor_id = slot.doctor_id
		date = slot.slot_date
		time = Time_segment.query.filter(Time_segment.t_seg_id == slot.slot_seg_id).first().t_seg_starttime
		medical_record = Medical_record(patient_id=patient_id)
		db.session.add(medical_record)
		db.session.commit()
		mc_id = medical_record.id
		application = Application(
					app_timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
					symptoms=symptom,
					status=StatusEnum.pending,
					reject_reason="",
					date=date,
					time=time,
					time_slot_id=time_slot_id,
					doctor_id=doctor_id,
					patient_id=patient_id,
					mc_id=mc_id)
		# update corresponding table
		db.session.add(application)
		timeslot = Time_slot.query.filter(Time_slot.id == time_slot_id).first()
		if timeslot.n_booked < timeslot.n_total:
			timeslot.n_booked = timeslot.n_booked + 1
		else:
			db.session.rollback()
			return make_response(jsonify({'ret':1, 'message':"no available slots!"}))
		db.session.commit()
		return make_response(jsonify({"ret":0, 'message':""}), 200)
	except:
		db.session.rollback()
		return make_response(jsonify({'ret':1, 'message':"error"}))

@app.route('/patientRecord',methods=['GET'])
def patientRecord():
	return render_template('/patientRecord.html')

@app.route('/patientFutureAppt', methods=['GET'])
@login_required
def patientFutureAppt():
	n_offset, n_tot_records, n_tot_page, page_count = helper.paginate(Application)
	patientID = current_user.get_id()
	total_number = len(Application.query.filter(Application.patient_id == patientID,
		Application.status == StatusEnum.approved,
		Application.date >= datetime.datetime.today()).order_by(Application.date.desc(),Application.time.desc()).all())
	apps = Application.query.filter(Application.patient_id == patientID,
		Application.status == StatusEnum.approved,
		Application.date >= datetime.datetime.today()).order_by(Application.date.desc(),Application.time.desc()).offset(n_offset-1).limit(page_count).all()
	helper.load_id2name_map()
	return make_response(
		jsonify({'total_number': total_number,
				"apps":[
				{"appID": app.id,
				"date": app.date.strftime(helper.DATE_FORMAT),
				"time": app.time.strftime(helper.TIME_FORMAT),
				"hospital":Hospital.query.filter(Hospital.id == helper.user2hosp(app.doctor_id, "doctor")).first().name,
				"department":helper.user2dept_name(app.doctor_id, "doctor"),
				"nurse": helper.id2name(app.approver_id),
				"patient": helper.id2name(app.patient_id),
				"doctor": helper.id2name(app.doctor_id),
				"symptoms": app.symptoms,
			} for app in apps]
			}))

@app.route('/getPatientRecord/', methods=['GET'])
@login_required
def getPatientRecord():
	type = request.args.get('type')
	if type == "appointment":
		n_offset, n_tot_records, n_tot_page, page_count = helper.paginate(Application)
		patientID = current_user.get_id()
		total_number = len(Application.query.filter(Application.patient_id == patientID).order_by(Application.date.desc(),Application.time.desc()).all())
		apps = Application.query.filter(Application.patient_id == patientID).order_by(Application.date.desc(),Application.time.desc()).offset(n_offset-1).limit(page_count).all()
		helper.load_id2name_map()
		return make_response(
			jsonify({'total_number': total_number,
					"apps":[
					{"appID": app.id,
					"date": app.date.strftime(helper.DATE_FORMAT),
					"time": app.time.strftime(helper.TIME_FORMAT),
					"hospital":Hospital.query.filter(Hospital.id == helper.user2hosp(app.doctor_id, "doctor")).first().name,
					"department":helper.user2dept_name(app.doctor_id, "doctor"),
					"nurse": helper.id2name(app.approver_id) if app.approver_id else "",
					"patient": helper.id2name(app.patient_id),
					"symptoms": app.symptoms,
					"doctor": helper.id2name(app.doctor_id),
					"status": app.status.value,
					"reject_reason":app.reject_reason,
				} for app in apps]
				}))
	elif type == "medical_record":
		n_offset, n_tot_records, n_tot_page, page_count = helper.paginate(Medical_record)
		patientID = current_user.get_id()
		apps = Application.query.filter(Application.patient_id == patientID,
							Application.Status == finished).order_by(Application.date.desc(),Application.time.desc()).offset(n_offset).limit(page_count).all()
		mcs = [Medical_record.query.filter(Medical_record.id==app.mc_id).first() for app in apps]
		helper.load_id2name_map()
		return make_response(
			jsonify({'total_number': n_tot_records,
					"mcs":[
					{"mcID": mcs[i].id,
					"date": apps[i].date.strftime(helper.DATE_FORMAT),
					"time": app[i].time.strftime(helper.TIME_FORMAT),
					"diagnosis": mcs[i].diagnosis} for i in range(len(mcs))]
					}))
	elif type == "personal_record":
		patientID = current_user.get_id()
		patient = Patient.query.filter(Patient.id== patientID).first()
		return make_response(
			jsonify([
			{
				"age": patient.age,
				"gender": patient.gender,
				"blood_type": patient.blood_type,
				"allergies": patient.allergies,
				"chronics": patient.chronics,
				"medications": patient.medications
			}
			]))


'''
@app.route('/patientGoViewMC', methods=['GET'])
@login_required
def patientGoViewMC():
	return render_template('patientViewMC.html'）

@app.route('/patientViewMC', methods=['POST'])
@login_required
def patientViewMC():
	return render_template('patientViewMC.html'）
'''
