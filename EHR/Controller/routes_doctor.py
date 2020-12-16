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

#---------------------------Doctor--------------------------------
#---------------------------Doctor--------------------------------
#---------------------------Doctor--------------------------------

#---doctor home page---
@app.route('/doctorHome', methods=['GET'])
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


	helper.load_id2name_map()
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
	if start_date == datetime.datetime.today().strftime(helper.DATE_FORMAT):
		filter = True
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
	if filter:
		for i in range(len(apps)):
			if datetime.datetime.combine(apps[i].date,apps[i].time) < datetime.datetime.now()-timedelta(minutes = 30):
				apps.pop(i)

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
