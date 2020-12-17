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
		return redirect("/loadHomePage")
	return render_template('nurseHome.html')


#---nurse all appointments page---
@app.route('/nurseAllAppt', methods=['GET', 'POST'])
@login_required
def nurseAllAppt():
	if not helper.check_nurse_privilege():
		return redirect("/loadHomePage")
	return render_template('nurseAllAppt.html')


#---under nurse home page---
@app.route('/nursePendingApp', methods=['GET', 'POST'])
# @login_required
def nursePendingApp():
	if not helper.check_nurse_privilege():
		return redirect("/loadHomePage")

	# look up Time_slot table for next 7 days time_slot id
	next7d_slotid = helper.day2slotid(period=7)
	nurse_id = current_user.get_id()
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
	if not helper.check_nurse_privilege():
		return redirect("/loadHomePage")

	nurseID = current_user.get_id()
	# department ID of current nurse
	today_depts_appts = helper.dept_appts(user=current_user, period=0).filter(Application.status==StatusEnum.approved).all()


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
	if not helper.check_nurse_privilege():
		return redirect("/loadHomePage")

	helper.load_id2name_map()
	nurse_id = current_user.get_id()
	nowtime = datetime.datetime.now()

	# filter1: today's appts； filter2: status=approved
	today_approved_appts = helper.dept_appts(user=current_user, period=0).\
		filter(
			Application.status == StatusEnum.approved
			).all()

	# filter2: now() in timeslot
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
		return redirect("/loadHomePage")

	nurse_id = current_user.get_id()
	start_date = datetime.datetime.strptime(request.form['startDate'], helper.DATE_FORMAT)
	start_date_str = request.form['startDate']
	today_str = datetime.datetime.strftime(datetime.datetime.now(), helper.DATE_FORMAT)

	if request.form['endDate']:
		end_date = datetime.datetime.strptime(request.form['endDate'], helper.DATE_FORMAT)
		future_appt_filter = helper.dept_appts(user=current_user, direction="future", period=(end_date-start_date).days, start_date=start_date).filter(Application.status==StatusEnum.approved)
		if start_date_str == today_str:
			nowTime = datetime.datetime.strftime(datetime.datetime.today(), helper.TIME_FORMAT)
			future_appts = future_appt_filter.filter(Application.time>=nowTime).all()
		else:
			future_appts = future_appt_filter.all()
	else:
		future_appt_filter = helper.dept_appts(user=current_user, direction="future", start_date=start_date).filter(Application.status==StatusEnum.approved)
		if start_date_str == today_str:
			nowTime = datetime.datetime.strftime(datetime.datetime.today(), helper.TIME_FORMAT)
			future_appts = future_appt_filter.filter(Application.time>=nowTime).all()
		else:
			future_appt_filter.all()


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


@app.route('/nursePastAppt', methods=['POST'])
def nursePastAppt():
	if not helper.check_nurse_privilege():
		return redirect("/loadHomePage")

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


@app.route('/nurseRejectedApp', methods=['POST'])
def nurseRejectedApp():
	if not helper.check_nurse_privilege():
		return redirect("/loadHomePage")

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
			apps = helper.dept_appts(user=current_user, direction="future",
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
	if not helper.check_nurse_privilege():
		return redirect("/loadHomePage")
	return render_template('nurseCreateAppt.html')


@app.route('/nurseGetDepartmentsForNurse',methods=['GET'])
@login_required
def nurseGetDepartmentsForNurse():
	if not helper.check_nurse_privilege():
		return redirect("/loadHomePage")

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
		return redirect("/loadHomePage")
	deptID = request.form['deptID']
	return make_response(jsonify(helper.dept_to_doc(deptID)), 200)



@app.route('/nurseGetSlotsForDoctor',methods=['POST'])
@login_required
def nurseGetSlotsForDoctor():
	if not helper.check_nurse_privilege():
		return redirect("/loadHomePage")

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
		return redirect("/loadHomePage")

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
		return redirect("/loadHomePage")

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
		return redirect("/loadHomePage")

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


# get lab report metadata
@app.route('/nurseGetLabReports', methods=['POST'])
@app.route('/doctorGetLabReports', methods=['POST'])
def getLabReports():
	if not (helper.check_doctor_privilege() or helper.check_nurse_privilege()):
		return redirect("/loadHomePage")

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


# nurse edit appointment/medical record
@app.route('/nurseEditPreExam', methods=['GET','POST'])
def nurseEditPreExam():
	if not helper.check_nurse_privilege():
		return redirect("/loadHomePage")

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
		return redirect("/loadHomePage")

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
@app.route('/doctorNurseGoViewMC', methods=['POST'])
@login_required
def goViewMC():
	if not (helper.check_doctor_privilege() or helper.check_nurse_privilege()):
		return redirect("/loadHomePage")

	patient_id = request.form['patientID']

	helper.load_id2name_map()
	return render_template('doctorNurseViewMC.html',
				patientID=patient_id,
				patientName=helper.id2name(patient_id))


@app.route('/doctorNurseViewMC', methods=['POST'])
@login_required
def viewMC():
	if not (helper.check_doctor_privilege() or helper.check_nurse_privilege()):
		return redirect("/loadHomePage")

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
