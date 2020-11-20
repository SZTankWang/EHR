from flask import request
from sqlalchemy.sql.sqltypes import String
from EHR.model.models import *
import math 
import datetime
from operator import and_

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

def paginate(db_obj):
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

def day2slotid(period: int, start_day=datetime.date.today()):
	next_d_slotid = [ res.id for res in (
										  Time_slot.query.filter(
											  Time_slot.slot_date<=start_day+timedelta(days=period),
											  Time_slot.slot_date>=start_day)).all()]
	return next_d_slotid

# No Longer Necessary! since we added date and time in Application
# slotid2date = {}
# def load_slots():
# 	global slotid2date
# 	slots = Time_slot.query.all()
# 	segid2time = {seg.t_seg_id: seg.t_seg_starttime for seg in Time_segment.query.all()}
	
# 	for slot in slots:
# 		slotid2date[slot.id] = {"slot_date": slot.slot_date,
# 								"seg_starttime": segid2time[slot.slot_seg_id]}
# 	print("slotid2date:", slotid2date)

# def slot2time(slot_id:int):
# 	load_slots()
# 	slot_date = slotid2date[slot_id]['slot_date']
# 	seg_starttime = slotid2date[slot_id]['seg_starttime']
# 	return slot_date, seg_starttime	


id_name_map = None
def load_id2name_map():
	global id_name_map
	id_name_map = {u.id: u.first_name + " "+u.last_name \
					for u in User.query.all()}
	
def id2name(this_id:int)->String:
	# person = User.query.filter(User.id==this_id).first()
	person_name = id_name_map[this_id]
	return person_name


def nurse_dept_appts(nurseID, period, start_date=datetime.date.today()):
	"""
	check this nurse dept. all appointments, with specified time period
	"""
	deptID = Nurse.query.filter(Nurse.id==nurseID).first().department_id
	same_dept_appts = Application.query.\
					join(Doctor, Doctor.id==Application.doctor_id).\
					join(Time_slot, Time_slot.id==Application.time_slot_id).\
						filter(
							Doctor.department_id==deptID,
							Time_slot.slot_date>=start_date,
							Time_slot.slot_date<=start_date+timedelta(days=period))
	return same_dept_appts

def t_slotid2date(slot_id):
	slot_date = Time_slot.query.filter(Time_slot.id==slot_id).first().slot_date
	return slot_date

def t_slot2time(slot_id):
	slot_time = Time_segment.query.join(
		Time_slot, Time_segment.t_seg_id==Time_slot.slot_seg_id
	).filter(Time_slot.id==slot_id).first().t_seg_starttime
	return slot_time
