from datetime import datetime, timedelta
from inspect import indentsize
# from sqlalchemy.sql.schema import ForeignKey
from werkzeug.security import check_password_hash, generate_password_hash
from EHR import db, login
from flask_login import UserMixin # UserMixin conains four useful login function
								  # [https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins]
import enum
from sqlalchemy import Enum

@login.user_loader
def load_user(id):
    return User.query.get(id)
class Hospital(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	phone = db.Column(db.String(20))
	address = db.Column(db.Text(), nullable=False)
	description = db.Column(db.Text())
	#one-to-many relationship
	departments = db.relationship('Department', backref='hospital', lazy=True)

	def __repr__(self):
		return f'Hospital < id: {self.id}, name: {self.name}, \
			phone: {self.phone}, address: {self.address}, description: {self.description} >'


class Department(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	phone = db.Column(db.String(20))
	description = db.Column(db.Text())
	#foreign key
	hospital_id = db.Column(db.Integer(), \
		db.ForeignKey('hospital.id'), nullable=False, onupdate="CASCADE")
	#one-to-many relationship
	doctors = db.relationship('Doctor', backref='department', lazy=True)
	nurses = db.relationship('Nurse', backref='department', lazy=True)

	def __repr__(self):
		return f'Department < id: {self.id}, name: {self.title}, \
			phone: {self.phone}, description: {self.description}\
				hospital_id: {self.hospital_id} >'

# Enum Type example reference :
# https://stackoverflow.com/questions/58049679/can-i-have-array-enum-column-with-flask-sqlalchemy
class RoleEnum(enum.Enum):
	doctor = "doctor"
	nurse = "nurse"
	patient = "patient"
	admin = "admin"


class User(UserMixin, db.Model):
	# user_id = db.Column(db.String(100), primary_key=True)
	id = db.Column(db.String(100), primary_key=True)
	first_name = db.Column(db.String(100), nullable=False)
	last_name = db.Column(db.String(100), nullable=False)
	role = db.Column(db.Enum(RoleEnum), nullable=False) # should we set a default role? default=RoleEnum.patient
	email = db.Column(db.String(100))
	phone = db.Column(db.String(20))
	password_hash = db.Column(db.String(100), nullable=False)

	#one-to-one relationship
	doctors = db.relationship('Doctor', backref='user', lazy=True, cascade="all, delete")
	nurses = db.relationship('Nurse', backref='user', lazy=True, cascade="all, delete")
	patients = db.relationship('Patient', backref='user', lazy=True, cascade="all, delete")

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class Admin(db.Model):
	id = db.Column(db.String(100), db.ForeignKey('user.id'), primary_key=True, onupdate="CASCADE")
	def __repr__(self):
		return f'Admin < id: {self.id} >'
	


class Doctor(db.Model):
	id = db.Column(db.String(100), db.ForeignKey('user.id'), primary_key=True, onupdate="CASCADE")
	#foreign key
	# user_id = db.Column(db.String(100), db.ForeignKey('user.user_id'), nullable=False, unique=True, onupdate="CASCADE")
	department_id = db.Column(db.Integer(),\
		db.ForeignKey('department.id'), nullable=False, onupdate="CASCADE")

	#one-to-many relationship
	time_slots = db.relationship('Time_slot', backref='doctor', lazy=True)
	applications = db.relationship('Application', backref='doctor', lazy=True)


	def __repr__(self):
		return f'Doctor < license_id: {self.id} >'


class Nurse(db.Model):
	id = db.Column(db.String(100), db.ForeignKey('user.id'), primary_key=True, onupdate="CASCADE")
	#foreign key
	# user_id = db.Column(db.String(100), db.ForeignKey('user.user_id'), nullable=False, unique=True, onupdate="CASCADE")
	department_id = db.Column(db.Integer(), \
		db.ForeignKey('department.id'), nullable=False, onupdate="CASCADE")

	#one-to-many relationship
	applications = db.relationship('Application', backref='nurse', lazy=True)
	medical_records = db.relationship('Medical_record', backref='nurse', lazy=True)
	lab_reports = db.relationship('Lab_report', backref='nurse', lazy=True)

	def __repr__(self):
		return f'Nurse < id: {self.id} >'

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class GenderEnum(enum.Enum):
	male = 'male'
	female = 'female'

class Patient(db.Model):
	id = db.Column(db.String(100), db.ForeignKey('user.id'), primary_key=True, onupdate="CASCADE")
	#foreign key
	# user_id = db.Column(db.String(100), db.ForeignKey('user.user_id'), nullable=False, unique=True, onupdate="CASCADE")

	age = db.Column(db.SmallInteger())
	gender = db.Column(db.Enum(GenderEnum))
	blood_type = db.Column(db.String(10))
	allergies = db.Column(db.Text())

	#one-to-many relationship
	applications = db.relationship('Application', backref='patient', lazy=True)
	medical_records = db.relationship('Medical_record', backref='patient', lazy=True)
	lab_reports = db.relationship('Lab_report', backref='patient', lazy=True)


	def __repr__(self):
		return f'Patient < id: {self.id} >'

class Time_segment(db.Model):
	t_seg_id = db.Column(db.Integer(), primary_key=True)
	t_seg_starttime = db.Column(db.Time(), nullable=False)
	
	def __repr__(self):
		return f'Time_segment < t_seg_id: {self.t_seg_id}, t_seg_starttime: {self.t_seg_starttime} >'
	

class Time_slot(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	slot_date = db.Column(db.Date(), nullable=False)
	n_total = db.Column(db.Integer(), nullable=False)
	n_booked = db.Column(db.Integer())

	#foreign key
	slot_seg_id = db.Column(db.Integer(), db.ForeignKey('time_segment.t_seg_id'), nullable=False)
	doctor_id = db.Column(db.String(100), \
		db.ForeignKey('doctor.id'), nullable=False)

	#one-to-many relationship
	applications = db.relationship('Application', backref='time_slot', lazy=True)

	def __repr__(self):
		return f'Time_slot < id: {self.id}, slot_date: {self.slot_date}, \
			slot_seg_id: {self.slot_seg_id}, n_total: {self.n_total}, n_booked: {self.n_booked}, \
				doctor_id: {self.doctor_id} >'

class StatusEnum(enum.Enum):
	approved = 'approved'
	rejected = 'rejected'
	pending = 'pending'
	finished = 'finished'


class Application(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	app_timestamp = db.Column(db.TIMESTAMP())
	symptoms = db.Column(db.Text())
	status = db.Column(db.Enum(StatusEnum), nullable=False)
	reject_reason = db.Column(db.Text())
	date = db.Column(db.Date(), nullable=False)
	time = db.Column(db.Time(), nullable=False)

	#foreign key
	time_slot_id = db.Column(db.Integer(), \
		db.ForeignKey('time_slot.id'), nullable=False)
	doctor_id = db.Column(db.String(100), \
		db.ForeignKey('doctor.id'), nullable=False)
	approver_id = db.Column(db.String(100), \
		db.ForeignKey('nurse.id'))
	patient_id = db.Column(db.String(100), \
		db.ForeignKey('patient.id'), nullable=False)
	#one-to-one relationship
	medical_record = db.relationship('Medical_record', backref='application', uselist=False ,lazy=True)

	def __repr__(self):
		return f'Application < id: {self.id}, app_timestamp: {self.app_timestamp}, \
			status: {self.status}, time_slot_id: {self.time_slot_id}, approver_id: {self.approver_id}, \
				doctor_id: {self.doctor_id}, patient_id: {self.patient_id}, date: {self.date}, \
				time: {self.time} >'

class Medical_record(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	body_temperature = db.Column(db.Float(1))
	blood_pressure = db.Column(db.Float(1))
	heart_rate = db.Column(db.Integer())
	weight = db.Column(db.Float(1))
	state = db.Column(db.Enum('conscious', 'coma'), default="conscious")
	#foreign key
	patient_id = db.Column(db.String(100), \
		db.ForeignKey('patient.id'), nullable=False)
	appt_id = db.Column(db.Integer(), \
		db.ForeignKey('application.id'), nullable=False)
	nurse_id = db.Column(db.String(100), \
		db.ForeignKey('nurse.id'), nullable=False)
	#one-to-many relationship
	lab_reports = db.relationship('Lab_report', backref='medical_record', lazy=True)
	prescription = db.relationship('Prescription', backref='medical_record', lazy=True)

	def __repr__(self):
		return f'Medical_record < id: {self.id}, appt_id: {self.appt_id}, \
			nurse_id: {self.nurse_id}, patient_id: {self.patient_id} >'

class Prescription(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	medicine = db.Column(db.Text())
	dose = db.Column(db.Text())
	comments = db.Column(db.Text())
	#foreign key
	mc_id = db.Column(db.Integer(), \
		db.ForeignKey('medical_record.id'), nullable=False)

	def __repr__(self):
		return f'Prescription < id: {self.id}, mc_id: {self.mc_id} >'

class Lab_report_type(db.Model):
	type = db.Column(db.String(50), primary_key=True)
	description = db.Column(db.Text())
	#one-to-many relationship, one report type might contains sereval reports.
	lab_reports = db.relationship('Lab_report', backref='lab_report_type', lazy=True)
	def __repr__(self):
		return f'Lab_report_type < type: {self.type}, number of lab reports: {len(self.lab_reports)} >'

class Lab_report(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	file = db.Column(db.LargeBinary())
	comments = db.Column(db.Text())
	#foreign key
	lr_type = db.Column(db.String(50), \
		db.ForeignKey('lab_report_type.type'), nullable=False)
	mc_id = db.Column(db.Integer(), \
		db.ForeignKey('medical_record.id'), nullable=False)
	uploader_id = db.Column(db.String(100), \
		db.ForeignKey('nurse.id'), nullable=False)
	patient_id = db.Column(db.String(100), \
		db.ForeignKey('patient.id'), nullable=False)

	def __repr__(self):
		return f'Lab_report < id: {self.id}, (report_)type: {len(self.type)},\
			mc_id: {self.mc_id}, uploader_id: {self.uploader_id},\
				patient_id: {self.patient_id} >'


