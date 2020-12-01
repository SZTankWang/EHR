from sys import exec_prefix
import os

from flask import Flask, render_template, redirect, url_for, request, json, jsonify, session, flash, make_response, abort, send_from_directory
from flask.globals import current_app
from flask.signals import appcontext_tearing_down, request_finished
from flask_login.utils import logout_user
from flask_login import login_user, logout_user, current_user, login_required
import collections
from itertools import count


from datetime import timedelta
from time import strftime
from numpy.core.arrayprint import TimedeltaFormat
from numpy.lib.function_base import select
from sqlalchemy.util.langhelpers import methods_equivalent

from werkzeug.utils import secure_filename
from EHR import app, db, login
from EHR.model.models import *
from EHR.Controller import control_helper as helper
from EHR.Controller.control_helper import DATE_FORMAT, TIME_FORMAT, id2name

import datetime


#---------------------------Nurse--------------------------------
#---------------------------Nurse--------------------------------
#---------------------------Nurse--------------------------------

#---nurse home page---
@app.route('/nurseHome', methods=['GET', 'POST'])
@login_required
def nurseHome():
	return render_template('nurseHome.html')


#---nurse all appointments page---
@app.route('/nurseAllAppt', methods=['GET', 'POST'])
@login_required
def nurseAllAppt():
	return render_template('nurseAllAppt.html')


#---under nurse home page---
@app.route('/nursePendingApp', methods=['GET', 'POST'])
# @login_required
def nursePendingApp():
	# look up Time_slot table for next 7 days time_slot id
	next7d_slotid = helper.day2slotid(period=7)
	nurse_id = current_user.get_id()
	# nurse_id = '17711783'
	pending_app = helper.dept_appts(user=current_user, period=7).\
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
	# 							for testing purpose, set the 'period' to 20
	# department ID of current nurse
	today_depts_appts = helper.dept_appts(user=current_user, period=0).all()

	helper.load_id2name_map()
	def response_generator(app):
		return {"appID": app.id,
			"date": app.date.strftime(helper.DATE_FORMAT),
			"time": app.time.strftime(helper.TIME_FORMAT),
			"doctor": helper.id2name(app.doctor_id),
			"patient": helper.id2name(app.patient_id),
			"symptoms": app.symptoms}

	return make_response(jsonify(
				[response_generator(app) for app in today_depts_appts ]), 200)


#---under nurse all appointments page---
@app.route('/nurseOnGoingAppt', methods=['GET'])
def nurseOnGoingAppt():
	helper.load_id2name_map() # save this, only for development use
	nurse_id = current_user.get_id()
	nowtime = datetime.datetime.now()
	# testing data
	# nurse_id = '17711783'
	# nowtime = datetime.datetime.strptime("2020-11-21 12:00:00", "%Y-%m-%d %H:%M:%S")

	# filter1: today's appts； filter2: status=approved
	today_approved_appts = helper.dept_appts(user=current_user, period=0).\
		filter(
			Application.status == StatusEnum.approved
			).all()

	# filter3: now() in timeslot
	now_approved_appts = []
	for appt in today_approved_appts:
		appt_date_time = datetime.datetime.combine(appt.date, appt.time)
		if appt_date_time <= nowtime <= appt_date_time + timedelta(minutes=30):
			now_approved_appts.append(appt)
	return make_response(
		jsonify(
			[{
				"appID": appt.id,
				"date": appt.date.strftime(helper.DATE_FORMAT),
				"time": appt.time.strftime(helper.TIME_FORMAT),
				"doctor": helper.id2name(appt.doctor_id),
				"patient": helper.id2name(appt.patient_id),
				"symptoms": appt.symptoms} for appt in now_approved_appts]
	))


@app.route('/nurseFutureAppt', methods=['GET', 'POST'])
@login_required
def nurseFutureAppt():
	## TODO
	## TODO
	## TODO
	## TODO: POST method
	nurse_id = current_user.get_id()
	# nurseID = "17711783" # a working nurseID for testing purpose, set 'period' to 30
	# department ID of current nurse
	future_appts = helper.dept_appts(user=current_user, direction="future").all()

	helper.load_id2name_map()
	def response_generator(app):
		return {"appID": app.id,
			"date": app.date.strftime(helper.DATE_FORMAT),
			"time": app.time.strftime(helper.TIME_FORMAT),
			"doctor": helper.id2name(app.doctor_id),
			"patient": helper.id2name(app.patient_id),
			"symptoms": app.symptoms}
	return make_response(jsonify(
				[response_generator(app) for app in future_appts ]), 200)


@app.route('/nursePastAppt', methods=['GET', 'POST'])
def nursePastAppt():
	# testing data
	# start_date = datetime.datetime.strptime("2020-11-20", helper.DATE_FORMAT)
	# end_date = datetime.datetime.strptime('2020-12-30', helper.DATE_FORMAT)
	# nurse_id = "17711783"

	end_date = datetime.datetime.strptime(request.form['endDate'], helper.DATE_FORMAT)
	nurse_id = current_user.get_id()
	if request.form['startDate']:
		start_date = datetime.datetime.strptime(request.form['startDate'], helper.DATE_FORMAT)
		apps = helper.dept_appts(user=current_user, period=(end_date-start_date).days,\
			 start_date=start_date).filter(Application.status==StatusEnum.finished)
	else: # if startDate is None then get all past appts
		apps = helper.dept_appts(user=current_user, direction="past",\
			 start_date=end_date).filter(Application.status==StatusEnum.finished)

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


@app.route('/nurseRejectedApp', methods=['GET', 'POST'])
def nurseRejectedApp():
	# testing data
	# start_date = datetime.datetime.strptime("2020-11-20", helper.DATE_FORMAT)
	# end_date = datetime.datetime.strptime('2020-12-30', helper.DATE_FORMAT)
	# nurse_id = "17711783"
	nurse_id = current_user.get_id()
	start_date = request.form['startDate']
	end_date = request.form['endDate']
	if start_date:
		start_date = datetime.datetime.strptime(request.form['startDate'], helper.DATE_FORMAT)
	if end_date:
		end_date = datetime.datetime.strptime(request.form['endDate'], helper.DATE_FORMAT)

	if start_date:
		if end_date:
			apps = helper.dept_appts(user=current_user, period=(end_date-start_date).days,\
			 	start_date=start_date).filter(Application.status==StatusEnum.rejected)
		else:
			apps = helper.dept_appts(user=current_user, direction="future", period=(end_date-start_date).days,\
			 	start_date=start_date).filter(Application.status==StatusEnum.rejected)
	else:
		if end_date:
			apps = helper.dept_appts(user=current_user, direction="past", period=(end_date-start_date).days,\
			 	start_date=end_date).filter(Application.status==StatusEnum.rejected)
		else:
			apps = helper.dept_appts(user=current_user).filter(Application.status==StatusEnum.rejected)

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


#---nurse create appointment---
@app.route('/nurseGoCreateAppt', methods=['GET', 'POST'])
@login_required
def nurseGoCreateAppt():
	return render_template('nurseCreateAppt.html')


@app.route('/nurseGetDepartmentsForNurse',methods=['GET'])
@login_required
def nurseGetDepartmentsForNurse():
	nurseID = current_user.get_id()
	dept_list,dept_name = helper.nurse_hosp2dept(nurseID)
	return make_response(
		jsonify(
			[{"deptID": dept_list[i],
			"deptName": dept_name[i]} for i in range(len(dept_list))]),200)


@app.route('/nurseGetDoctorsForDepartment',methods=['GET','POST'])
@login_required
def nurseGetDoctorsForDepartment():
	deptID = request.form['deptID']
	return make_response(jsonify(helper.dept_to_doc(deptID)), 200)



@app.route('/nurseGetSlotsForDoctor',methods=['GET','POST'])
@login_required
def nurseGetSlotsForDoctor():
	doctorID = request.form['doctorID']
	slot_list = helper.doc2slots_available(doctorID, 0, start_date=datetime.date.today())
	date_list = [helper.t_slotid2date(slot_list[i].id) for i in range(len(slot_list))]
	time_list = [helper.t_slot2time(slot_list[i].id) for i in range(len(slot_list))]
	#JZ: datetime.combine???
	return make_response(
		jsonify(
			[{"slotID": str(slot_list[i].id),"slotDateTime": datetime.datetime.combine(date_list[i],time_list[i]).strftime("%Y-%m-%d %H:%M")}
			 for i in range(len(slot_list))]),200)


@app.route('/nurseCreateAppt', methods=['GET','POST'])
@login_required
def nurseCreateAppt():
	try:
		nurseID = current_user.get_id()
		symptom = request.form['symptoms']
		time_slot_id = request.form['slotID']
		doctor_id = request.form['doctorID']
		patient_id = request.form['patientID']
		slot = Time_slot.query.filter(Time_slot.id == time_slot_id).first()
		date = slot.slot_date
		time = Time_segment.query.filter(Time_segment.t_seg_id == slot.slot_seg_id).first().t_seg_starttime
		medical_record = Medical_record(patient_id=patient_id)
		db.session.add(medical_record)
		db.session.commit()
		mc_id = medical_record.id
		application = Application(
					app_timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
					symptoms=symptom,
					status=StatusEnum.approved,
					reject_reason="",
					date=date,
					time=time,
					time_slot_id=time_slot_id,
					doctor_id=doctor_id,
					approver_id=nurseID,
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


#---nurse process application---
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
		appt.reject_reason = request.form['comments']

	db.session.commit()

	return make_response({'ret':0})


#---nurse view appointment---
@app.route('/nurseGoViewAppt/<string:appID>', methods=['GET', 'POST'])
@login_required
def nurseGoViewAppt(appID):
	appt_res = Application.query.filter(Application.id==appID).first()
	finished = False
	if appt_res.status.value == "finished":
		finished = True

	helper.load_id2name_map()
	return render_template('nurseViewAppt.html',
		appID=appt_res.id,
		date=appt_res.date.strftime(helper.DATE_FORMAT),
		time=appt_res.time.strftime(helper.TIME_FORMAT),
		doctor=helper.id2name(appt_res.doctor_id),
		patientID=appt_res.patient_id,
		patient=helper.id2name(appt_res.patient_id),
		symptoms=appt_res.symptoms,
		comments=appt_res.reject_reason,
		mcID=appt_res.mc_id,
		finished=finished)


@app.route('/nurseViewAppt', methods=['GET','POST'])
@app.route('/doctorViewAppt', methods=['GET','POST'])
@app.route('/doctorNurseViewAppt', methods=['GET','POST'])
@login_required
def doctorNurseViewAppt():
	if request.method == "POST":
		mc_id = request.form['mcID']
	elif request.method == "GET":
		mc_id = request.args.get('mcID')
	mc = Medical_record.query.filter(Medical_record.id==mc_id).first()
	if not mc:
		return make_response({"ret": "Medical Record Not Found!"})
	prescription_list = Prescription.query.filter(Prescription.mc_id==mc_id).all()
	lab_reports = mc.lab_reports

	ret = {
		"ret": "0",

		"preExam":
			{"bodyTemperature": str(mc.body_temperature),
			"heartRate": str(mc.heart_rate),
			"lowBloodPressure": str(mc.low_blood_pressure),
			"highBloodPressure": str(mc.high_blood_pressure),
			"weight": str(mc.weight),
			"height": str(mc.height),
			"state": mc.state.value},

		"diagnosis":
			mc.diagnosis,

		"prescriptions":
			[{"id": pres.id,
			  "medicine": pres.medicine,
			  "dose": pres.dose,
			  "comments": pres.comments} for pres in prescription_list],

		"labReports":
			[{"lr_type": lr.lr_type,
			"id": lr.id,
			"doctor_comments": lr.doctor_comment,
			"nurse_comments": lr.nurse_comment,
			"file_path": lr.file_path} for lr in lab_reports]
	}

	getLabReportTypes = bool(request.form['type'])
	if getLabReportTypes:
		lab_r_types = Lab_report_type.query.all()

		ret["labReportTypes"] = [{"type": lrt.type,
		  "description": lrt.description
		} for lrt in lab_r_types]

	return make_response(jsonify(ret))

#JZ
@app.route('/nurseGetLabReports', methods=['POST'])
@app.route('/doctorGetLabReports', methods=['POST'])
def getLabReports():
	mc_id = request.form['mcID']
	mc = Medical_record.query.filter(Medical_record.id==mc_id).first()
	if not mc:
		return make_response({"ret": "Medical Record Not Found!"})
	return make_response(jsonify({
		"ret": 0,
		"labReports":
			[{"lr_type": lr.lr_type,
			"id": lr.id,
			"nurse_comments": lr.nurse_comment,
			"doctor_comments": lr.doctor_comment,
			"file_path": lr.file_path} for lr in mc.lab_reports]
		}))


@app.route('/previewOneLR/<path:filename>')
def previewLR(filename):
	return send_from_directory(app.config["UPLOAD_FOLDER"],filename)
	# lr_id = request.form['lrID']
	# mc = Medical_record.query.filter(Medical_record.id==lr_id).first()
	# return make_response(jsonify({'file_path': mc.file_path}))


#---nurse edit appointment/medical record---
@app.route('/nurseEditPreExam', methods=['GET','POST'])
def nurseEditPreExam():
	mc_id = request.form['mcID']
	body_temperature = helper.StrOrNone(request.form['bodyTemperature'])
	heart_rate = helper.StrOrNone(request.form['heartRate'])
	high_blood_pressure = helper.StrOrNone(request.form['highBloodPressure'])
	low_blood_pressure = helper.StrOrNone(request.form['lowBloodPressure'])
	weight = helper.StrOrNone(request.form['weight'])
	height = helper.StrOrNone(request.form['height'])
	state = stateEnum(request.form['state'])

	mc = Medical_record.query.filter( Medical_record.id == mc_id).first()
	mc.body_temperature = body_temperature
	mc.heart_rate = heart_rate
	mc.high_blood_pressure = high_blood_pressure
	mc.low_blood_pressure = low_blood_pressure
	mc.weight = weight
	mc.height = height
	mc.state = state

	db.session.commit()

	return make_response(jsonify({'ret':0}))

#JZ
@app.route('/nurseUploadLabReport', methods=['GET', 'POST'])
@login_required
def nurseUploadLabReport():
	nurse_id = current_user.get_id()

	mc_id = request.form['mcID']
	lr_id = request.form['id']
	lab_report_file = request.files['labReportInput']
	filename = lab_report_file.filename
	file_path = None
	if filename != "":
		# file_name = os.path.splitext(lr_fname)[0]
		file_ext = os.path.splitext(filename)[1]
		if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
			abort(400)
		lr_fname = secure_filename(mc_id+"_"+filename)
		file_path = os.path.join("EHR", app.config["UPLOAD_FOLDER"], lr_fname)
		lab_report_file.save(file_path)
	nurse_comments = request.form['commentsInput']

	lab_report = Lab_report.query.get(lr_id)
	if not lab_report:
		return make_response(jsonify({"ret": "Lab report request deos not exist"}))
	lab_report.nurse_comment = nurse_comments
	lab_report.uploader_id = nurse_id
	lab_report.file_path = lr_fname

	db.session.commit()

	return make_response(jsonify({"ret": 0}))


#---nurse view medical record---
@app.route('/doctorNurseGoViewMC', methods=['GET', 'POST'])
@login_required
def goViewMC():
	patient_id = request.form['patientID']
	helper.load_id2name_map()
	return render_template('doctorNurseViewMC.html',
				patientID=patient_id,
				patientName=helper.id2name(patient_id))


@app.route('/doctorNurseViewMC', methods=['GET', 'POST'])
@login_required
def viewMC():
	patient_id = request.form['patientID']
	helper.load_id2name_map()
	table = Application.query.filter(Application.patient_id==patient_id,Application.status==StatusEnum.finished).all()
	return make_response(
		jsonify({'patientID':str(patient_id),
			'patientName':helper.id2name(patient_id),
		'appts':[{'appID':str(table[i].id),
		'mcID':table[i].mc_id,
		'date':table[i].date.strftime(helper.DATE_FORMAT),
		'time':table[i].time.strftime(helper.TIME_FORMAT),
		'doctor':helper.id2name(table[i].doctor_id),
		'symptoms':table[i].symptoms}
		for i in range(len(table))]}
		       )
	)


#---------------------------Doctor--------------------------------
#---------------------------Doctor--------------------------------
#---------------------------Doctor--------------------------------

#---doctor home page---
@app.route('/doctorHome', methods=['GET', 'POST'])
@login_required
def doctorHome():
	return render_template('doctorHome.html')


@app.route('/doctorOnGoingAppt', methods=['GET', 'POST'])
@login_required
def doctorOnGoingAppt():
	helper.load_id2name_map() # save this, only for development use
	doctorID = current_user.get_id()
	nowtime = datetime.datetime.now()
	appt_list = helper.doc2appts(doctorID,0)

	now_approved_appts = []
	for appt in appt_list:
		appt_date_time = datetime.datetime.combine(appt.date, appt.time)
		if appt_date_time <= nowtime <= appt_date_time + timedelta(minutes=30):
			now_approved_appts.append(appt)
	return make_response(
		jsonify(
			[{
				"appID": appt.id,
				"date": appt.date.strftime(helper.DATE_FORMAT),
				"time": appt.time.strftime(helper.TIME_FORMAT),
				"patient": helper.id2name(appt.approver_id),
				"patient": helper.id2name(appt.patient_id),
				"symptoms": appt.symptoms} for appt in now_approved_appts]
	))

@app.route('/doctorTodayAppt', methods=['GET', 'POST'])
@login_required
def doctorTodayAppt():
	doctorID = current_user.get_id()
	appt_list = helper.doc2appts(doctorID,0)
	helper.load_id2name_map()
	return make_response(
		jsonify([{"appID":str(appt_list[i].id),
				"date":appt_list[i].date.strftime(helper.DATE_FORMAT),
				"time":appt_list[i].time.strftime(helper.TIME_FORMAT),
				"nurse":helper.id2name(appt_list[i].approver_id),
				"patient":helper.id2name(appt_list[i].patient_id),
				"symptoms":appt_list[i].symptoms}
		for i in range(len(appt_list))]
		       )
	)


#---doctor all appointments page---
@app.route('/doctorAllAppt', methods=['GET', 'POST'])
@login_required
def doctorAllAppt():
	return render_template('doctorAllAppt.html')


@app.route('/doctorFutureAppt', methods=['GET', 'POST'])
@login_required
def doctorFutureAppt():
	if request.method == "POST":
		start_date = request.form["startDate"]
		end_date = request.form["endDate"]
	elif request.method == "GET":
		start_date = 0
		end_date = 0
	doctorID = current_user.get_id()
	if start_date:
		start_date = datetime.datetime.strptime(start_date, helper.DATE_FORMAT)
	else:
		start_date = datetime.datetime.today()
	if end_date:
		end_date = datetime.datetime.strptime(end_date, helper.DATE_FORMAT)

	if end_date:
		apps = helper.doc2appts(doctorID,period=(end_date-start_date).days,start_date = start_date)
	else:
		apps = helper.doc2appts(doctorID,start_date = start_date,limit = 'no')

	helper.load_id2name_map()
	return make_response(
		jsonify([
			{
				"appID": app.id,
				"date": app.date.strftime(helper.DATE_FORMAT),
				"time": app.time.strftime(helper.TIME_FORMAT),
				"nurse": helper.id2name(app.approver_id),
				"patient": helper.id2name(app.patient_id),
				"symptoms": app.symptoms,
			} for app in apps
		]))


@app.route('/doctorPastAppt', methods=['GET', 'POST'])
@login_required
def doctorPastAppt():
	if request.method == "POST":
		start_date = request.form["startDate"]
		end_date = request.form["endDate"]
	elif request.method == "GET":
		start_date = 0
		end_date = 0
	doctorID = current_user.get_id()
	if start_date:
		start_date = datetime.datetime.strptime(start_date, helper.DATE_FORMAT)
	if end_date:
		end_date = datetime.datetime.strptime(end_date, helper.DATE_FORMAT)
	else:
		end_date = datetime.date.today()

	if start_date:
		apps = helper.doc2appts(doctorID,period=(end_date-start_date).days,direction = 'past',start_date = end_date)
	else:
		apps = helper.doc2appts(doctorID,start_date = start_date, direction = 'past',limit = 'no')

	helper.load_id2name_map()
	return make_response(
		jsonify([
			{
				"appID": app.id,
				"date": app.date.strftime(helper.DATE_FORMAT),
				"time": app.time.strftime(helper.TIME_FORMAT),
				"nurse": helper.id2name(app.approver_id),
				"patient": helper.id2name(app.patient_id),
				"symptoms": app.symptoms,
			} for app in apps
		]))



#---doctor schedule page---
@app.route('/doctorSchedule', methods=['GET', 'POST'])
@login_required
def doctorSchedule():
	return render_template('doctorSchedule.html')


#---doctor view appt---
@app.route('/doctorGoViewAppt/<string:appID>', methods=['GET', 'POST'])
@login_required
def doctorGoViewAppt(appID):
	appt_res = Application.query.filter(Application.id==appID).first()
	finished = False
	if appt_res.status.value == "finished":
		finished = True

	return render_template('doctorViewAppt.html',
		appID=appt_res.id,
		date=appt_res.date.strftime(helper.DATE_FORMAT),
		time=appt_res.time.strftime(helper.TIME_FORMAT),
		approverID=appt_res.approver_id,
		patientID=appt_res.patient_id,
		patient=helper.id2name(appt_res.patient_id),
		symptoms=appt_res.symptoms,
		comments=appt_res.reject_reason,
		mcID=appt_res.mc_id,
		finished=finished)


@app.route('/doctorGetPrescrip', methods=['POST'])
def doctorGetPrescrip():
	mc_id = request.form['mcID']
	mc = Medical_record.query.filter(Medical_record.id==mc_id).first()
	if not mc:
		return make_response({"ret": "Medical Record Not Found!"})
	prescription_list = Prescription.query.filter(Prescription.mc_id==mc_id).all()
	return make_response(jsonify({
		"ret": 0,
		"prescriptions":
			[{"id": pres.id,
			  "medicine": pres.medicine,
			  "dose": pres.dose,
			  "comments": pres.comments} for pres in prescription_list]
		}))

@app.route('/doctorEditDiag', methods=['POST'])
def doctorEditDiag():
	mc_id = request.form['mcID']
	diagnosis = request.form['diagnosis']
	mc = Medical_record.query.filter(Medical_record.id==mc_id).first()
	if not mc:
		return make_response({"ret": "Medical Record Not Found!"})
	mc.diagnosis = diagnosis
	try:
		db.session.commit()
	except:
		db.session.rollback()
		return make_response(jsonify({'ret': "Database error"}))
	return make_response(jsonify({'ret':0}))

@app.route('/doctorAddPrescrip', methods=['POST'])
def doctorAddPrescrip():
	mc_id = request.form['mcID']
	medicine = request.form['medicine']
	dose = request.form['dose']
	comments = request.form['comments']
	prescription = Prescription(
				medicine = medicine,
				dose = dose,
				comments = comments,
				mc_id = mc_id
	)
	try:
		db.session.add(prescription)
		db.session.commit()
	except:
		db.session.rollback()
		return make_response(jsonify({'ret':1, 'message': "Database error"}))
	return make_response(jsonify({'ret':0}))

@app.route('/doctorReqLabReport', methods=['POST'])
def doctorReqLabReport():
	mc_id = request.form['mcID']
	patient_id = Medical_record.query.filter(Medical_record.id==mc_id).first().patient_id
	lr_type = request.form['type']
	# lr_type = labReportTypeEnum[lr_type_str.lower().replace(" ", "_")]
	comments = request.form['comments']
	lab_report = Lab_report(
				doctor_comment = comments,
				lr_type = lr_type,
				mc_id = mc_id,
				patient_id = patient_id
	)
	try:
		db.session.add(lab_report)
		db.session.commit()
	except:
		db.session.rollback()
		return make_response(jsonify({'ret': "Database error"}))
	return make_response(jsonify({'ret':0}))

@app.route('/doctorFinishAppt', methods=['POST'])
def doctorFinishAppt():
	app_id = request.form['appID']
	appt = Application.query.filter(Application.id==app_id).first()
	appt.status = StatusEnum.finished
	db.session.commit()
	return make_response(jsonify({'ret':0}))


#---------------------------Util--------------------------------
#---------------------------Util--------------------------------
#---------------------------Util--------------------------------
@app.route('/getPatientInfo', methods=['POST'])
def getPatientInfo():
	p_id = request.form['patientID']
	patient = db.session.query(Patient).filter(Patient.id==p_id).first()
	gender = patient.gender
	if gender:
		gender = gender.value
	return make_response(jsonify({"ret": 0, "age": patient.age, "gender": gender, "bloodType": patient.blood_type, "allergies": patient.allergies, "chronics": patient.chronics, "medications": patient.medications}), 200)


#---get comments util---
@app.route('/getComments', methods=['GET','POST'])
def getComments():
	app_id = request.form['appID']
	appt = Application.query.filter(Application.id==app_id).one()
	return make_response(jsonify({"comments":appt.reject_reason, "status":appt.status.value}))


#------------------------------common functionalities-------------------------------
#------------------------------common functionalities-------------------------------
#------------------------------common functionalities-------------------------------
#--- edit personal information ---
@app.route('/nurseSettings', methods=['GET'])
@app.route('/doctorSettings', methods=['GET'])
@app.route('/patientSettings', methods=['GET'])
def Settings():
	id = current_user.get_id()
	hospital_id = 1
	user, role_user = None, None
	print(current_user.role)

	if current_user.role == RoleEnum.patient:
		user, role_user = db.session.query(User, Patient).join(User).filter(User.id==id).first()
		return render_template("patientSettings.html",
					firstName=user.first_name,
					lastName=user.last_name,
					nationalID=role_user.id,
					email=user.email,
					phone=user.phone)

	elif current_user.role == RoleEnum.nurse:
		user, role_user = db.session.query(User, Nurse).join(User).filter(User.id==id).first()
	elif current_user.role == RoleEnum.doctor:
		user, role_user = db.session.query(User, Doctor).join(User).filter(User.id==id).first()

	return render_template("doctorNurseSettings.html",
					hospitalID=hospital_id,
					deptID=role_user.department_id,
					firstName=user.first_name,
					lastName=user.last_name,
					licenseID=user.id,
					email=user.email,
					phone=user.phone)


@app.route('/patientUpdateHealthInfo', methods=['GET', 'POST'])
def patientUpdateHealthInfo():
	p_id = current_user.get_id()
	if request.method == "GET":
		role_user = db.session.query(Patient).filter(Patient.id==p_id).first()
		gender = role_user.gender
		if gender:
			gender = gender.value
		return make_response(jsonify({"ret": 0, "age": role_user.age, "gender": gender, "bloodType": role_user.blood_type, "allergies": role_user.allergies, "chronics": role_user.chronics, "medications": role_user.medications}))
	if request.method == "POST":
		age = helper.StrOrNone(request.form['age'])
		gender = request.form['gender']
		blood_type = request.form['bloodType']
		allergies = request.form['allergies']
		chronics = request.form['chronics']
		medications = request.form['medications']
		db.session.query(Patient).filter(Patient.id==p_id).update(
			{
				Patient.id: p_id,
				Patient.gender: gender,
				Patient.allergies: allergies,
				Patient.age: age,
				Patient.blood_type: blood_type,
				Patient.chronics: chronics,
				Patient.medications: medications

			}, synchronize_session=False
		)
		db.session.commit()
		return make_response(jsonify({"ret": 0}))

@app.route('/doctorNurseUpdateInfo', methods=['POST'])
@app.route('/patientUpdateInfo', methods=['POST'])
def UpdateInfo():
	try:
		f_name = request.form['firstName']
		l_name = request.form['lastName']
		old_id = current_user.get_id()
		new_id = request.form['id']
		email = request.form['email']
		phone = request.form['phone']
		role_user = None
		user = None
		if current_user.role == RoleEnum.doctor:
			user, role_user = db.session.query(User, Doctor).join(User).filter(User.id==old_id).first()
		elif current_user.role == RoleEnum.nurse:
			user, role_user = db.session.query(User, Nurse).join(User).filter(User.id==old_id).first()
		elif current_user.role == RoleEnum.patient:
			user, role_user = db.session.query(User, Patient).join().filter(User.id==old_id).first()
		if not role_user or not user:
			return make_response(jsonify({'ret':"user not found"}))

		# user.id = new_id
		# print("user.id", user.id)
		user.first_name = f_name
		user.last_name= l_name
		user.email= email
		user.phone = phone
		db.session.commit()

		# return make_response(jsonify({'ret':0, 'firstName': f_name, "lastName": l_name, "id": new_id, "email": email, "phone": phone}), 200)
		return make_response(jsonify({'ret':0}), 200)
	except:
		db.session.rollback()
		return make_response(jsonify({'ret':1}))



#------------------------------Admin-------------------------------
#------------------------------Admin-------------------------------
#------------------------------Admin-------------------------------
@app.route('/addHospital',methods=['POST'])
def addHospital():

	name = helper.get_from_form(request, 'name')
	phone = helper.get_from_form(request, 'phone')
	address = helper.get_from_form(request, 'address')
	description = helper.get_from_form(request, 'description')

	# check for duplicated hospital name
	res = Hospital.query.filter(Hospital.name == name).all()
	if res != []:
		return make_response(jsonify({'ret':1, 'msg':'Duplicated Hospital Name'}))

	hos = Hospital(
		name=name,
		phone=phone,
		address=address,
		description=description
	)
	try:
		db.session.add(hos)
		db.session.commit()
	except:
		db.session.rollback()
		return make_response(jsonify({'ret':1, 'message': "Database error"}))

	return make_response(jsonify({'ret':0}))

@app.route('/addLabReportType', methods=['POST'])
def addLabReportType():
	lr_type_value = helper.get_from_form(request, 'type')
	lr_description = helper.get_from_form(request, 'description')
	# lr_type_value = "Good Test"
	# lr_type_name = lr_type_value.lower().replace(" ", "_")
	# class labReportTypeEnum(enum.Enum):
	# 	lr_type_name = lr_type_value
	lr_type = Lab_report_type(
		type = lr_type_value,
		description = lr_description
	)
	db.session.add(lr_type)
	db.session.commit()
	return make_response(jsonify({'ret':0}))
