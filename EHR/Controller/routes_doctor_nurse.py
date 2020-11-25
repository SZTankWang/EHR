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
from EHR.model.models import *
from EHR.Controller import control_helper as helper
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
	today_approved_appts = helper.nurse_dept_appts(nurseID=nurse_id, period=0).\
		filter(
			Application.status==StatusEnum.approved
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
	future_appts = helper.nurse_dept_appts(nurse_id, direction="future").all()

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
		apps = helper.nurse_dept_appts(nurseID=nurse_id, period=(end_date-start_date).days,\
			 start_date=start_date).filter(Application.status==StatusEnum.finished)
	else: # if startDate is None then get all past appts
		apps = helper.nurse_dept_appts(nurseID=nurse_id, direction="past",\
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
			apps = helper.nurse_dept_appts(nurseID=nurse_id, period=(end_date-start_date).days,\
			 	start_date=start_date).filter(Application.status==StatusEnum.rejected)
		else:
			apps = helper.nurse_dept_appts(nurseID=nurse_id, direction="future", period=(end_date-start_date).days,\
			 	start_date=start_date).filter(Application.status==StatusEnum.rejected)
	else:
		if end_date:
			apps = helper.nurse_dept_appts(nurseID=nurse_id, direction="past", period=(end_date-start_date).days,\
			 	start_date=end_date).filter(Application.status==StatusEnum.rejected)
		else:
			apps = helper.nurse_dept_appts(nurseID=nurse_id).filter(Application.status==StatusEnum.rejected)

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
		appID = request.form['id']
		symptom = request.form['symptoms']
		time_slot_id = request.form['time_slot_id']
		doctor_id = request.form['doctor_id']
		patient_id = request.form['patient_id']
		slot = Time_slot.query.filter(Time_slot.id == time_slot_id).first()
		date = slot.slot_date
		time = Time_segment.query.filter(Time_segment.t_seg_id == slot.slot_seg_id).first().t_seg_starttime
		medical_record = Medical_record(patient_id=patient_id)
		mc_id = medical_record.mc_id
		application = Application(
					id=appID,
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
		db.session.add(medical_record)
		timeslot = Time_slot.query.filter(id == time_slot_id).first()
		if timeslot.n_booked > 0:
			timeslot.n_booked = timeslot.n_booked - 1
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
@login_required
def nurseViewAppt():
	mc_id = request.form['mcID']
	mc = Medical_record.query.filter(Medical_record.id==mc_id).first()
	if not mc:
		return make_response({"ret": "Medical Record Not Found!"})
	prescription_list = Prescription.query.filter(Prescription.mc_id==mc_id).all()
	lab_reports = mc.lab_reports
	if bool(request.form['type']):
		lab_r_types = Lab_report_type.query.all()

		return make_response(
			jsonify({
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

				"labReportTypes":
					[{"type": lrt.type.value,
					  "description": lrt.description
						} for lrt in lab_r_types],

				"labReports":
					[{"lr_type": lr.lr_type.value,
					"id": lr.id,
					"comments": lr.comments} for lr in lab_reports]
			})
		)
	else:
		return make_response(
			jsonify({
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
					[{"lr_type": lr.lr_type.value,
					"id": lr.id,
					"comments": lr.comments} for lr in lab_reports]
			})
		)


@app.route('/nursePreviewLR', methods=['GET', 'POST'])
def nursePreviewLR():
	lr_id = request.form['lrID']
	mc = Medical_record.query.filter(Medical_record.id==lr_id).first()


#---nurse edit appointment/medical record---
@app.route('/nurseEditPreExam', methods=['GET','POST'])
def nurseEditPreExam():
	mc_id = request.form['mcID']
	body_temperature = request.form['bodyTemperature']
	heart_rate = request.form['heartRate']
	high_blood_pressure = request.form['highBloodPressure']
	low_blood_pressure = request.form['lowBloodPressure']
	weight = request.form['weight']
	height = request.form['height']
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


@app.route('/nurseUploadLabReport', methods=['GET', 'POST'])
@login_required
def nurseUploadLabReport():
	nurse_id = current_user.get_id()

	mc_id = request.form['mcID']
	lr_type_id = request.form['type']
	lab_report_file = request.files['labReport'].read()
	comments = request.form['comments']

	mc = Medical_record.query.filter(Medical_record.id==mc_id).first()
	patient_id = mc.patient_id

	lab_report = Lab_report(
		comments=comments,
		lr_type = lr_type_id,
		uploader_id=nurse_id,
		patient_id=patient_id,
		mc_id=mc_id,
		file=lab_report_file
	)
	mc.lab_reports.append(lab_report)
	db.session.add(lab_report)
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
		'date':table[i].date.strftime("%Y-%m-%d"),
		'time':table[i].time.strftime("%H:%M"),
		'doctor':helper.id2name(table[i].doctor_id),
		'symptoms':table[i].symptoms}
		for i in range(len(table))]}
		       )
	)


#---------------------------Doctor--------------------------------
#---------------------------Doctor--------------------------------
#---------------------------Doctor--------------------------------
#TODO
#TODO
#TODO

#---doctor home page---
@app.route('/doctorHome', methods=['GET', 'POST'])
@login_required
def doctorHome():
	return render_template('doctorHome.html')


@app.route('/doctorOnGoingAppt', methods=['GET', 'POST'])
@login_required
def doctorOnGoingAppt():
	pass


@app.route('/doctorTodayAppt', methods=['GET', 'POST'])
@login_required
def doctorTodayAppt():
	pass


#---doctor all appointments page---
@app.route('/doctorAllAppt', methods=['GET', 'POST'])
@login_required
def doctorAllAppt():
	return render_template('doctorAllAppt.html')


@app.route('/doctorFutureAppt', methods=['GET', 'POST'])
@login_required
def doctorFutureAppt():
	pass


@app.route('/doctorPastAppt', methods=['GET', 'POST'])
@login_required
def doctorPastAppt():
	pass





#---------------------------Util--------------------------------
#---------------------------Util--------------------------------
#---------------------------Util--------------------------------

#---get comments util---
@app.route('/getComments', methods=['GET','POST'])
def getComments():
	app_id = request.form['appID']
	appt = Application.query.filter(Application.id==app_id).one()
	return make_response(jsonify({"comments":appt.reject_reason, "status":appt.status.value}))
