from datetime import date, timedelta
from random import randint
import sys
from sys import path_importer_cache
from typing import Container, DefaultDict, List

from sqlalchemy.orm.session import _state_session
# sys.path.append("/Users/qing/School_Study/2020_Fall/SE/PROJECT/EHR")
# mypath = "/Users/qing/School_Study/2020_Fall/SE/PROJECT/EHR/EHR/utilities"
sys.path.append("/Users/jenny/Desktop/EHR")
mypath = "/Users/jenny/Desktop/EHR/EHR/utilities"
from EHR.model.models import *
from EHR import db
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup, NavigableString
import datetime
from sqlalchemy import func, or_
from EHR.Controller import control_helper as helper
import string

N_RECORD = 100
USER_N_RECORD = 500
BLOOD_TYPE = ['A','B','O','AB']
TIME_SLOT_START_TIME = '0001-01-01-09-00-00' # only "09-00-00" part matters
TIME_SLOT_START_DATE = '2020-11-20'
MEDICINE_LIST = [ 'Vicodin', 'Simvastatin', 'Lisinopril', 'Levothyroxine', \
				  'Azithromycin', 'Metformin', 'Lipitor', 'Amlodipine', \
				  'Amoxicillin', 'Hydrochlorothiazide']
lab_report_types = ['Complete Blood Count', 'Basic Metabolic Panel', 'Lipid Panel', 'Liver Panel', 'Urinalysis']


def gen_hospital_data():
	hospital_df = pd.read_csv(mypath + "/hospital_info.csv")
	name_list, address_list = hospital_df["name"].tolist(), hospital_df["address"].tolist()
	phone_list = ['{:8}'.format(random.randint(10000000,99999999)) for _ in range(N_RECORD)]
	start_index = Hospital.query.count()
	for i in range(start_index, start_index+N_RECORD):
		h = Hospital(id=i+1, name=name_list[i], phone=phone_list[i], address=address_list[i])
		try:
			db.session.add(h)
			db.session.commit()
		except:
			continue
	print("gen_hospital_data DONE")

def get_dept_list():
	res = requests.get("https://www.netdoctor.co.uk/health-services/nhs/a4502/a-to-z-of-hospital-departments/")
	soup = BeautifulSoup(res.content, 'html.parser')
	name_descp = {}
	for dept_name in soup.find_all('h2',{'class':'body-h2'}):
		name_descp[dept_name.text] = ''
		for para in dept_name.next_siblings:
			if para.name != 'p':
				break
			if isinstance(para, NavigableString):
				continue
			name_descp[dept_name.text] += para.text
			# if para.next_sibling.name == 'ul':
			#     print(para.next_sibling)
			#     print()
	# dept_df = pd.DataFrame({'dept_name': list(name_descp.keys()), 'dept_description':list(name_descp.values())})
	# dept_df.to_csv("/Users/qing/School_Study/2020_Fall/SE/project/SE_Fall2020_EHR/utilities/dept_info.csv")
	return name_descp

def gen_user_data():
	#  hospital info
	user_df = pd.read_csv(mypath + "/user_info.csv")
	# id_list = list(set(['{:8}'.format(random.randint(10000000,99999999)) for _ in range(USER_N_RECORD)  ]))
	roles = ['doctor', 'nurse', 'patient']

	firstname_list, lastname_list, email_list, password_list = \
		user_df["first_name"].tolist(), user_df["last_name"], user_df["email"].tolist(), user_df["password"].tolist()
	phone_list = ['{:8}'.format(random.randint(10000000,99999999)) for _ in range(USER_N_RECORD)]
	num_dept = Department.query.count()
	print("num_dept==================", num_dept)

	for i in range(1, USER_N_RECORD):
		u = User(id=i,
				 first_name=firstname_list[i],
				 last_name=lastname_list[i],
				 role=roles[i%3],
				#  role=roles[i%2],
				 email=email_list[i],
				 phone=phone_list[i])
		u.set_password('1')
		db.session.add(u)

		if u.role=='doctor':
			new = Doctor(id=i,
					   department_id=1+(i%num_dept))
		elif u.role=='patient':
			new = Patient(id=i,
						  age=random.randint(1,100),
						  gender=random.choice(list(GenderEnum)),
						  blood_type=random.choice(BLOOD_TYPE))
		elif u.role=='nurse':
			new = Nurse(id=i,
						department_id=1+(i%num_dept))
		# elif u.role=='admin':
		# 	new = Admin(id=0)

		db.session.add(new)
	db.session.commit()
	print("gen_user_data DONE")

def gen_dept_data():
	name_desc_df = pd.read_csv(mypath + "/dept_info.csv")
	dept_phones = ["{:8}".format(random.randint(10000000,99999999)) for _ in range(len(name_desc_df))]
	name_list = name_desc_df['dept_name'].tolist()
	desp_list = name_desc_df['dept_description'].tolist()
	for i in range(len(name_desc_df)):
		d = Department(id=i+1, title=name_list[i], description=desp_list[i], phone=dept_phones[i], hospital_id='8')
		db.session.add(d)

	db.session.commit()
	print("gen_dept_data DONE")


def gen_time_seg():
	office_hour_s = 80000
	# doctor_id_list = get_single_column(Doctor, Doctor.id)

	for i in range(18-9):
		office_hour_s += 10000
		ts = Time_segment(
					   t_seg_starttime="{:06}".format(office_hour_s))
		db.session.add(ts)
	db.session.commit()
	print("gen_time_seg DONE")

def gen_time_slot():

	date_format= '%Y-%m-%d'
	# time_format= '%H-%M-%S'
	# datetime_format = date_format+'-'+time_format

	# start_date = datetime.date.today()
	# start_date = datetime.datetime.strptime(TIME_SLOT_START_DATE, date_format)
	start_date = datetime.date.today()
	start_index = Time_slot.query.count()
	n_tot_slot = Time_segment.query.count()
	doctor_list = Doctor.query.filter(or_(Doctor.department_id==26,Doctor.department_id==1)).all()
	for i in range(start_index, start_index+1000):
		# work-day decision below, not necessary, but leave it here just in case
		# while not random_date or random_date.weekday() > 5:
		#     random_date = start_date + timedelta(days=random.randint(1,7))
		random_date = start_date + timedelta(days=random.randint(0,10))
		n_total = random.randint(1,3)
		doctor_id = random.choice(doctor_list).id
		slot_seg_id = random.randint(1,n_tot_slot)

		check_exist = Time_slot.query.filter(
			Time_slot.doctor_id==doctor_id,
			Time_slot.slot_seg_id == slot_seg_id
		).first()
		if check_exist:
			continue

		print(doctor_id, i)
		ts = Time_slot(
					   slot_date=random_date,
					   slot_seg_id=slot_seg_id,
					   n_total=n_total,
					   n_booked=random.randint(0,n_total),
					   doctor_id=doctor_id)
		db.session.add(ts)
	db.session.commit()
	print("gen_time_slot DONE")

def get_single_column(db_obj, column_wanted) -> List:
	return [res[0] for res in db_obj.query.with_entities(column_wanted).all()]


def gen_appt():
	slotid_list = get_single_column(Time_slot, Time_slot.id)
	basetime = datetime.datetime.today()
	# status_list = [status for status, _ in StatusEnum.__members__.items()]
	# doctorid_list = get_single_column(Doctor, Doctor.id)
	nurseid_list = get_single_column(Nurse, Nurse.id)
	mcid_list = Medical_record.query.all()
	patientid_list = get_single_column(Patient, Patient.id)
	base_date = datetime.date.today()

	for i in range(N_RECORD):
		# initialize two date variales
		appt_tobe_date = base_date + timedelta(days=random.randint(0,7))
		appt_made_time = basetime + timedelta(days=random.randint(-14,14))

		# enforce to make appointment at leat 1 day ahead
		while appt_tobe_date < appt_made_time.date():
			appt_tobe_date = appt_tobe_date + timedelta(days=random.randint(0,7))
			appt_made_time = appt_made_time + timedelta(days=random.randint(-14,14))
		status_enum = random.choice(list(StatusEnum))
		tslotid = random.choice(slotid_list)
		timeslot_filter = Time_slot.query.filter(Time_slot.id==tslotid)
		doctorid = Time_slot.query.filter(Time_slot.id==tslotid).first().doctor_id
		patientid = random.choice(patientid_list)
		# for those appts with status=approved, generate a new medical_record
		mc_count=None
		if status_enum == StatusEnum.approved:
			mc_count = Medical_record.query.count()
			mc = Medical_record(
				id = mc_count+1,
				body_temperature = random.uniform(30,45),
				low_blood_pressure = random.randint(60,90),
				high_blood_pressure = random.randint(80,120),
				heart_rate = random.randint(60,100),
				weight = random.uniform(0,200),
				height = random.uniform(150,200),
				state = random.choice(list(stateEnum)),
				diagnosis = "doctor diagnosis: ...",
				patient_id = patientid
			)
			db.session.add(mc)

		appt = Application(
						doctor_id = doctorid,
						app_timestamp = appt_made_time,
						# status = status_enum.value,
						status = status_enum,
						time_slot_id = tslotid,
						approver_id = random.choice(nurseid_list) if status_enum == StatusEnum.approved else None,
						patient_id = patientid,
						symptoms = random.choice(["fever","dry cough","tiredness","sore throat"]),
						date = timeslot_filter.one().slot_date,
						time = helper.segid2time(timeslot_filter.one().slot_seg_id),
						mc_id = mc_count+1 if mc_count!=None else None
		)
		if mc_count != None:
			mc.appointment.append(appt)
		db.session.add(appt)
	db.session.commit()
	print("gen_appt DONE")

def gen_prescription():
	mcid_list = [mc.id for mc in Medical_record.query.all()]
	for _ in range(N_RECORD):
		medicine = " & ".join(random.choices(MEDICINE_LIST, k=random.randint(0, len(MEDICINE_LIST))))
		prscrpt = Prescription(
				medicine=medicine,
				dose = 0 if medicine=="" else random.randint(1,5),
				comments = "Drink hot water, Take good pills",
				mc_id = random.choice(mcid_list)
		)
		db.session.add(prscrpt)
	db.session.commit()
	print("gen_prescription DONE")

def gen_random_string(times, length):
	letters = string.ascii_lowercase
	str_list = []
	for _ in range(times):
		random_str = ''.join(random.choice(letters) for i in range(length))
		str_list.append(random_str)
	return str_list

def gen_report_type():
	n_type = len(lab_report_types)
	descriptions = gen_random_string(n_type, 30)
	for i in range(n_type):
		lrt = Lab_report_type(
			type=lab_report_types[i],
			description=descriptions[i]
		)
		db.session.add(lrt)
	db.session.commit()
	print("gen_report_type DONE")

def gen_lab_reports():
	# rp_file = open("/Users/qing/School_Study/2020_Fall/SE/PROJECT/EHR/EHR/utilities/sample_lab_report.pdf", "rb").read()
	mc_ids = [mc.id for mc in Medical_record.query.all()]
	nurse_ids = [n.id for n in Nurse.query.all()]
	patient_ids = [p.id for p in Patient.query.all()]

	for i in range(N_RECORD):
		lb = Lab_report(
			lr_type = random.choice(lab_report_types),
			doctor_comment = gen_random_string(1, 30),
			nurse_comment = gen_random_string(1, 30),
			mc_id = random.choice(mc_ids),
			uploader_id = random.choice(nurse_ids),
			patient_id = random.choice(patient_ids),
			file_path=None
		)
		db.session.add(lb)
	db.session.commit()
	print("gen_lab_reports DONE")



def practice_query():
	slot_id=15
	slot_date = Time_slot.query.filter(Time_slot.id==slot_id).first().slot_date
	seg_id = Time_slot.query.filter(Time_slot.id==slot_id).first().slot_seg_id
	seg_start_t = Time_segment.query.filter(Time_segment.t_seg_id==seg_id).first().t_seg_starttime


def main():
	# please do not change the following execution order
	print("on it")
	gen_hospital_data()
	gen_dept_data()
	gen_user_data()
	gen_time_seg()
	gen_time_slot()
	gen_appt()
	gen_prescription()
	gen_report_type()
	# gen_lab_reports()

main()
