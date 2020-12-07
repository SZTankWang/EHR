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
#from flask import current_app as app
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
	if not helper.check_nurse_privilege():
		return redirect("/login")
	return render_template('nurseHome.html')


#---nurse all appointments page---
@app.route('/nurseAllAppt', methods=['GET', 'POST'])
@login_required
def nurseAllAppt():
	if not helper.check_nurse_privilege():
		return redirect("/login")
	return render_template('nurseAllAppt.html')


#---under nurse home page---
@app.route('/nursePendingApp', methods=['GET', 'POST'])
# @login_required
def nursePendingApp():
	if not helper.check_nurse_privilege():
		return redirect("/login")

	# look up Time_slot table for next 7 days time_slot id
	next7d_slotid = helper.day2slotid(period=7)
	nurse_id = current_user.get_id()
	pending_app = helper.dept_appts(user=current_user, period=7).\
									filter(
										Application.status==StatusEnum.pending,
										Application.time_slot_id.in_(next7d_slotid)).all()
	# helper.load_id2name_map()
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
	if not helper.check_nurse_privilege():
		return redirect("/login")

	nurseID = current_user.get_id()
	# department ID of current nurse
	today_depts_appts = helper.dept_appts(user=current_user, period=0).all()

	# helper.load_id2name_map()
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
	if not helper.check_nurse_privilege():
		return redirect("/login")

	# helper.load_id2name_map() # save this, only for development use
	nurse_id = current_user.get_id()
	nowtime = datetime.datetime.now()

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
	if not helper.check_nurse_privilege():
		return redirect("/login")

	nurse_id = current_user.get_id()
	start_date = datetime.datetime.strptime(request.form['startDate'], helper.DATE_FORMAT)
	if request.form['endDate']:
		end_date = datetime.datetime.strptime(request.form['endDate'], helper.DATE_FORMAT)
		future_appts = helper.dept_appts(user=current_user, direction="future", period=(end_date-start_date).days, start_date=start_date).all()
	else:
		future_appts = helper.dept_appts(user=current_user, direction="future", start_date=start_date).all()

	# helper.load_id2name_map()
	def response_generator(app):
		return {"appID": app.id,
			"date": app.date.strftime(helper.DATE_FORMAT),
			"time": app.time.strftime(helper.TIME_FORMAT),
			"doctor": helper.id2name(app.doctor_id),
			"patient": helper.id2name(app.patient_id),
			"symptoms": app.symptoms}
	return make_response(jsonify(
				[response_generator(app) for app in future_appts ]), 200)


@app.route('/nursePastAppt', methods=['POST'])
def nursePastAppt():
	if not helper.check_nurse_privilege():
		return redirect("/login")

	end_date = datetime.datetime.strptime(request.form['endDate'], helper.DATE_FORMAT)
	nurse_id = current_user.get_id()
	if request.form['startDate']:
		start_date = datetime.datetime.strptime(request.form['startDate'], helper.DATE_FORMAT)
		apps = helper.dept_appts(user=current_user, period=(end_date-start_date).days,\
			 start_date=start_date).filter(Application.status==StatusEnum.finished)
	else: # if startDate is None then get all past appts
		apps = helper.dept_appts(user=current_user, direction="past",\
			 start_date=end_date).filter(Application.status==StatusEnum.finished)

	# helper.load_id2name_map()
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


@app.route('/nurseRejectedApp', methods=['POST'])
def nurseRejectedApp():
	if not helper.check_nurse_privilege():
		return redirect("/login")

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

	# helper.load_id2name_map()
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
	if not helper.check_nurse_privilege():
		return redirect("/login")
	return render_template('nurseCreateAppt.html')


@app.route('/nurseGetDepartmentsForNurse',methods=['GET'])
@login_required
def nurseGetDepartmentsForNurse():
	if not helper.check_nurse_privilege():
		return redirect("/login")

	nurseID = current_user.get_id()
	dept_list,dept_name = helper.nurse_hosp2dept(nurseID)
	return make_response(
		jsonify(
			[{"deptID": dept_list[i],
			"deptName": dept_name[i]} for i in range(len(dept_list))]),200)


@app.route('/nurseGetDoctorsForDepartment',methods=['POST'])
@login_required
def nurseGetDoctorsForDepartment():
	if not helper.check_nurse_privilege():
		return redirect("/login")
	deptID = request.form['deptID']
	return make_response(jsonify(helper.dept_to_doc(deptID)), 200)



@app.route('/nurseGetSlotsForDoctor',methods=['POST'])
@login_required
def nurseGetSlotsForDoctor():
	if not helper.check_nurse_privilege():
		return redirect("/login")

	doctorID = request.form['doctorID']
	slot_list = helper.doc2slots_available(doctorID, 0, start_date=datetime.date.today())
	date_list = [helper.t_slotid2date(slot_list[i].id) for i in range(len(slot_list))]
	time_list = [helper.t_slot2time(slot_list[i].id) for i in range(len(slot_list))]
	return make_response(
		jsonify(
			[{"slotID": str(slot_list[i].id),"slotDateTime": datetime.datetime.combine(date_list[i],time_list[i]).strftime("%Y-%m-%d %H:%M")}
			 for i in range(len(slot_list))]),200)


# nurse create a new appointment for in-person patients
@app.route('/nurseCreateAppt', methods=['POST'])
@login_required
def nurseCreateAppt():
	if not helper.check_nurse_privilege():
		return redirect("/login")

	try:
		nurseID = current_user.get_id()
		symptom = request.form['symptoms']
		time_slot_id = request.form['slotID']
		doctor_id = request.form['doctorID']
		patient_id = request.form['patientID']
		slot = Time_slot.query.filter(Time_slot.id == time_slot_id).first()
		date = slot.slot_date
		time = Time_segment.query.filter(Time_segment.t_seg_id == slot.slot_seg_id).first().t_seg_starttime

		# create an empty medical record for the to-be-created appointment
		medical_record = Medical_record(patient_id=patient_id)
		try:
			db.session.add(medical_record)
			db.session.commit()
		except:
			db.session.rollback()
			return make_response(jsonify({'ret':"error"}))
		mc_id = medical_record.id

		# create the appointment (approved application)
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
		db.session.add(application)

		# update time slot
		timeslot = Time_slot.query.filter(Time_slot.id == time_slot_id).first()
		if timeslot.n_booked < timeslot.n_total:
			timeslot.n_booked = timeslot.n_booked + 1
		else:
			db.session.rollback()
			db.session.delete(medical_record)
			db.session.commit()
			return make_response(jsonify({'ret':"no available slots!"}))
		db.session.commit()
		return make_response(jsonify({"ret":0}), 200)
	except:
		db.session.rollback()
		return make_response(jsonify({'ret':"Database error"}))


# nurse process application
@app.route('/nurseProcessApp', methods=['POST'])
def nurseProcessApp():
	if not helper.check_nurse_privilege():
		return redirect("/login")

	try:
		nurseID = current_user.get_id()
		appID = request.form['appID']
		# get Appt
		app = Application.query.filter(Application.id==appID).first()
		if not app:
			return {'ret': f'The application: {appID} does not exist!'}

		decision = request.form['action']
		app.approver_id = nurseID
		app.reject_reason = request.form['comments']
		if decision.lower() == 'reject':
			app.status = StatusEnum.rejected
			timeslot = Time_slot.query.filter(Time_slot.id == app.time_slot_id).first()
			if timeslot.n_booked > 0:
				timeslot.n_booked = timeslot.n_booked - 1
		elif decision.lower() == 'approve':
			app.status = StatusEnum.approved
			medical_record = Medical_record(patient_id=app.patient_id)
			try:
				db.session.add(medical_record)
				db.session.commit()
			except:
				db.session.rollback()
				return make_response(jsonify({'ret':"error"}))
			# link medical record to appointment
			mc_id = medical_record.id
			app.mc_id = mc_id

		db.session.commit()
		return make_response({'ret':0})
	except:
		db.session.rollback()
		return make_response(jsonify({'ret':"Database error"}))


# nurse view appointment
@app.route('/nurseGoViewAppt/<string:appID>', methods=['GET', 'POST'])
@login_required
def nurseGoViewAppt(appID):
	if not helper.check_nurse_privilege():
		return redirect("/login")

	appt_res = Application.query.filter(Application.id==appID).first()
	finished = False
	if appt_res.status.value == "finished":
		finished = True

	# helper.load_id2name_map()
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
	if not (helper.check_doctor_privilege() or helper.check_nurse_privilege()):
		return redirect("/login")

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

	# get the lab report types for doctor for lab report request creation
	if request.form['type'] == "1":
		if not helper.check_doctor_privilege():
			return make_response({"ret": "Access to lab report types not granted"})

		lab_r_types = Lab_report_type.query.all()

		ret["labReportTypes"] = [{"type": lrt.type,
		  "description": lrt.description
		} for lrt in lab_r_types]

	return make_response(jsonify(ret))

# get lab report metadata
@app.route('/nurseGetLabReports', methods=['POST'])
@app.route('/doctorGetLabReports', methods=['POST'])
def getLabReports():
	if not (helper.check_doctor_privilege() or helper.check_nurse_privilege()):
		return redirect("/login")

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

# open lab report in a new tab
@app.route('/previewOneLR/<path:filename>')
def previewLR(filename):
	return send_from_directory(app.config["UPLOAD_FOLDER"],filename)


# nurse edit appointment/medical record
@app.route('/nurseEditPreExam', methods=['GET','POST'])
def nurseEditPreExam():
	if not helper.check_nurse_privilege():
		return redirect("/login")

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

	try:
		db.session.commit()
		return make_response(jsonify({'ret':0}))
	except:
		db.session.rollback()
		return make_response(jsonify({'ret':"Database error"}))

#JZ
@app.route('/nurseUploadLabReport', methods=['GET', 'POST'])
@login_required
def nurseUploadLabReport():
	if not helper.check_nurse_privilege():
		return redirect("/login")

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

	try:
		db.session.commit()
		return make_response(jsonify({'ret':0}))
	except:
		db.session.rollback()
		return make_response(jsonify({'ret':"Database error"}))


#---view medical record---
@app.route('/doctorNurseGoViewMC', methods=['GET', 'POST'])
@login_required
def goViewMC():
	if not (helper.check_doctor_privilege() or helper.check_nurse_privilege()):
		return redirect("/login")

	patient_id = request.form['patientID']
	# helper.load_id2name_map()
	return render_template('doctorNurseViewMC.html',
				patientID=patient_id,
				patientName=helper.id2name(patient_id))


@app.route('/doctorNurseViewMC', methods=['GET', 'POST'])
@login_required
def viewMC():
	if not (helper.check_doctor_privilege() or helper.check_nurse_privilege()):
		return redirect("/login")

	patient_id = request.form['patientID']
	# helper.load_id2name_map()
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
	if not helper.check_doctor_privilege():
		return redirect("/login")
	return render_template('doctorHome.html')


@app.route('/doctorOnGoingAppt', methods=['GET', 'POST'])
@login_required
def doctorOnGoingAppt():
	if not helper.check_doctor_privilege():
		return redirect("/login")

	# elper.load_id2name_map() # save this, only for development use
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
	if not helper.check_doctor_privilege():
		return redirect("/login")

	doctorID = current_user.get_id()
	appt_list = helper.doc2appts(doctorID,0)

	# helper.load_id2name_map()
	return make_response(
		jsonify([{"appID":str(appt_list[i].id),
				"date":appt_list[i].date.strftime(helper.DATE_FORMAT),
				"time":appt_list[i].time.strftime(helper.TIME_FORMAT),
				"nurse":helper.id2name(appt_list[i].approver_id),
				"patient":helper.id2name(appt_list[i].patient_id),
				"symptoms":appt_list[i].symptoms}
		for i in range(len(appt_list))])
	)


#---doctor all appointments page---
@app.route('/doctorAllAppt', methods=['GET', 'POST'])
@login_required
def doctorAllAppt():
	if not helper.check_doctor_privilege():
		return redirect("/login")

	return render_template('doctorAllAppt.html')


@app.route('/doctorFutureAppt', methods=['GET', 'POST'])
@login_required
def doctorFutureAppt():
	if not helper.check_doctor_privilege():
		return redirect("/login")

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

	# helper.load_id2name_map()
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
	if not helper.check_doctor_privilege():
		return redirect("/login")

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

	# helper.load_id2name_map()
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
@app.route('/doctorSchedule', methods=['GET'])
@login_required
def doctorSchedule():
	if not helper.check_doctor_privilege():
		return redirect("/login")

	return render_template('doctorSchedule.html')

@app.route('/doctorNewSlot', methods=['POST'])
@login_required
def doctorNewSlot():
	if not helper.check_doctor_privilege():
		return redirect("/login")

	doctor_id = current_user.get_id()
	date = datetime.datetime.strptime(request.form['date'], "%m/%d/%Y")
	startTime = datetime.datetime.strptime(request.form['startTime'], helper.TIME_FORMAT)
	total_slots = request.form['slotNumber']
	t_seg = Time_segment.query.filter(Time_segment.t_seg_starttime==startTime).one()

	exist_slot = Time_slot.query.filter(
		Time_slot.doctor_id == doctor_id,
		Time_slot.slot_seg_id == t_seg.t_seg_id,
		Time_slot.slot_date == date
	).first()
	if exist_slot:
		return make_response({'ret':1, 'msg':'Slot Already Created'})

	time_slot = Time_slot(slot_date=date, n_total=total_slots, n_booked=0, slot_seg_id=t_seg.t_seg_id,  doctor_id=doctor_id)
	db.session.add(time_slot)
	try:
		db.session.commit()
		return make_response(jsonify({'ret':0}))
	except:
		db.session.rollback()
		return make_response(jsonify({'ret':"Database error"}))

	return make_response({"ret": 0})

@app.route('/doctorGetSlots', methods=['GET'])
@login_required
def doctorGetSlots():
	if not helper.check_doctor_privilege():
		return redirect("/login")

	doctor_id = current_user.get_id()
	t_slots = Time_slot.query.filter(Time_slot.doctor_id==doctor_id).all()

	ret = {
		"ret": 0,
		"data": [
			{
				"title": f'total: {item.n_total}, booked: {item.n_booked}',
				"start": item.slot_date.strftime(helper.DATE_FORMAT) + "T" + Time_segment.query.filter(Time_segment.t_seg_id==item.slot_seg_id).one().t_seg_starttime.strftime(helper.TIME_FORMAT)
			}
			for item in t_slots
		]
	}

	return make_response(jsonify(ret), 200)


#---doctor view appt---
@app.route('/doctorGoViewAppt/<string:appID>', methods=['GET', 'POST'])
@login_required
def doctorGoViewAppt(appID):
	if not helper.check_doctor_privilege():
		return redirect("/login")

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
	if not helper.check_doctor_privilege():
		return redirect("/login")

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
	if not helper.check_doctor_privilege():
		return redirect("/login")

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
	if not helper.check_doctor_privilege():
		return redirect("/login")

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
	db.session.add(prescription)

	try:
		db.session.commit()
		return make_response(jsonify({'ret':0}))
	except:
		db.session.rollback()
		return make_response(jsonify({'ret': "Database error"}))


@app.route('/doctorReqLabReport', methods=['POST'])
def doctorReqLabReport():
	if not helper.check_doctor_privilege():
		return redirect("/login")

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

	db.session.add(lab_report)

	try:
		db.session.commit()
		return make_response(jsonify({'ret':0}))
	except:
		db.session.rollback()
		return make_response(jsonify({'ret': "Database error"}))


@app.route('/doctorFinishAppt', methods=['POST'])
def doctorFinishAppt():
	if not helper.check_doctor_privilege():
		return redirect("/login")

	app_id = request.form['appID']
	appt = Application.query.filter(Application.id==app_id).first()
	appt.status = StatusEnum.finished
	try:
		db.session.commit()
		return make_response(jsonify({'ret':0}))
	except:
		db.session.rollback()
		return make_response(jsonify({'ret': "Database error"}))



#---------------------------Util--------------------------------
#---------------------------Util--------------------------------
#---------------------------Util--------------------------------
@app.route('/getPatientInfo', methods=['POST'])
def getPatientInfo():
	if not (helper.check_doctor_privilege() or helper.check_doctor_privilege()):
		return redirect("/login")

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
