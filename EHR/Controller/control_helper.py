from flask import request
from sqlalchemy.sql.sqltypes import String
from EHR.model.models import *
import math 
import datetime
from operator import and_


def pageinate(db_obj):
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

def futureday_slotid(period: int, start_day=datetime.date.today()):
	next_d_slotid = [ res.id for res in (
										  Time_slot.query.filter(and_(Time_slot.slot_date<=start_day+datetime.timedelta(days=period),
										  Time_slot.slot_date>=start_day)).all())]
	return next_d_slotid

def slot2time(slot_id:int):
	slot_date = Time_slot.query.filter(
				Time_slot.id==slot_id).first().slot_date 

	seg_id = Time_slot.query.filter(
				Time_slot.id==slot_id).first().slot_seg_id 

	seg_start_t = Time_segment.query.filter(
				Time_segment.t_seg_id==seg_id).first().t_seg_starttime

	return slot_date, seg_start_t	

def id2name(this_id:int)->String:
	id_name_map = {u.id: u.first_name + " "+u.last_name \
					for u in User.query.all()}
	# person = User.query.filter(User.id==this_id).first()
	person_name = id_name_map[this_id]
	return person_name
