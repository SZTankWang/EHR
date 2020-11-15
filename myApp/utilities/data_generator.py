from datetime import date, timedelta
import sys
from sys import path_importer_cache
from typing import DefaultDict, List
sys.path.append("/Users/qing/School_Study/2020_Fall/SE/project/")
from SE_Fall2020_EHR.models import *
# from SE_Fall2020_EHR.models import db
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup, NavigableString
import datetime
from sqlalchemy import func


N_RECORD = 100
BLOOD_TYPE = ['A','B','O','AB']
TIME_SLOT_START_TIME = '0001-01-01-09-00-00' # only "09-00-00" part matters
TIME_SLOT_START_DATE = '2020-11-30'

def gen_hospital_data():


    hospital_df = pd.read_csv("/Users/qing/School_Study/2020_Fall/SE/project/SE_Fall2020_EHR/utilities/hospital_info.csv")
    hospital_df = pd.read_csv("/Users/qing/School_Study/2020_Fall/SE/project/SE_Fall2020_EHR/utilities/hospital_info.csv")
    name_list, address_list = hospital_df["name"].tolist(), hospital_df["address"].tolist()
    phone_list = ['{:8}'.format(random.randint(10000000,99999999)) for _ in range(n_record)]
    start_index = Hospital.query.count()
    for i in range(start_index, start_index+N_RECORD):
        h = Hospital(id=i+1, name=name_list[i], phone=phone_list[i], address=address_list[i])
        db.session.add(h)
    db.session.commit()

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
    dept_df = pd.DataFrame({'dept_name': list(name_descp.keys()), 'dept_description':list(name_descp.values())})
    # dept_df.to_csv("/Users/qing/School_Study/2020_Fall/SE/project/SE_Fall2020_EHR/utilities/dept_info.csv")
    return name_descp

def gen_user_data():
    #  hospital info   
    user_df = pd.read_csv("/Users/qing/School_Study/2020_Fall/SE/project/SE_Fall2020_EHR/utilities/user_info.csv")
    id_list = list(set(['{:8}'.format(random.randint(10000000,99999999)) for _ in range(n_record)  ]))
    roles = ['doctor', 'nurse', 'patient']
    role_list = [roles[i%len(roles)] for i in range(N_RECORD)]
    
    firstname_list, lastname_list, email_list, password_list = \
        user_df["first_name"].tolist(), user_df["last_name"], user_df["email"].tolist(), user_df["password"].tolist()
    phone_list = ['{:8}'.format(random.randint(10000000,99999999)) for _ in range(n_record)]
    num_dept = Department.query.count()

    for i in range(N_RECORD):
        u = User(id=id_list[i],
                 first_name=firstname_list[i],
                 last_name=lastname_list[i],
                 role=role_list[i],
                 email=email_list[i],
                 phone=phone_list[i])
        u.set_password(password_list[i])
        db.session.add(u)

        if u.role=='doctor':
            new = Doctor(id=id_list[i],
                       department_id=1+i%num_dept)
        elif u.role=='patient':
            new = Patient(id=id_list[i], 
                          age=random.randint(1,100), 
                          gender=random.choice(list(GenderEnum)), 
                          blood_type=random.choice(BLOOD_TYPE))
        elif u.role=='nurse':
            new = Nurse(id=id_list[i],
                        department_id=1+i%num_dept)
        elif u.role=='admin':
            new = Admin(id=id_list[i])



        db.session.add(new)
    db.session.commit()

def gen_dept_data():    
    name_desc_df = pd.read_csv("/Users/qing/School_Study/2020_Fall/SE/project/SE_Fall2020_EHR/utilities/dept_info.csv")
    dept_phones = ["{:8}".format(random.randint(10000000,99999999)) for _ in range(len(name_desc_df))]
    name_list = name_desc_df['dept_name'].tolist()
    desp_list = name_desc_df['dept_description'].tolist()
    # counter = 0
    for i in range(len(name_desc_df)):
        d = Department(id=i+1, title=name_list[i], description=desp_list[i], phone=dept_phones[i], hospital_id='8')
        # counter += 1

        db.session.add(d)
    db.session.commit()

def gen_time_slot():
    
    date_format= '%Y-%m-%d'
    time_format= '%H-%M-%S'
    datetime_format = date_format+'-'+time_format

    # start_date = datetime.date.today()    
    start_date = datetime.datetime.strptime(TIME_SLOT_START_DATE, date_format)
    office_start_hour = datetime.datetime.strptime(TIME_SLOT_START_TIME, datetime_format)
    start_index = Time_slot.query.count()
    for i in range(start_index, start_index+30):
        # generate random date
        # random_date = None
        # while not random_date or random_date.weekday() > 5:
        #     random_date = start_date + timedelta(days=random.randint(1,7))
        random_date = start_date + timedelta(days=random.randint(1,7))

        # generate random start hour of time slot 
        random_start_time = (office_start_hour+ timedelta(hours=random.randint(0,7))).time()

        dc = Doctor.query.order_by(func.random()).first()
        n_total = random.randint(0,2)
        ts = Time_slot(id=i+1,
                       slot_date=random_date,
                       slot_start_time=random_start_time,
                       n_total=n_total,
                       n_booked=random.randint(0,n_total),
                       doctor_id=dc.id)
        db.session.add(ts)
    db.session.commit()

def get_single_column(db_obj, column_wanted) -> List:
    return [res[0] for res in db_obj.query.with_entities(column_wanted).all()]

def gen_appt():
    slotid_list = get_single_column(Time_slot, Time_slot.id) 
    appt_base_time = datetime.datetime.now()
    status_list = [status for status, _ in StatusEnum.__members__.items()]
    doctorid_list = get_single_column(Doctor, Doctor.id)
    nurseid_list = get_single_column(Nurse, Nurse.id)
    patientid_list = get_single_column(Patient, Patient.id)
    for _ in range(N_RECORD):
        appt_random_time = appt_base_time + random.random()*datetime.timedelta(days=10)
        appt = Application( 
                        app_timestamp = appt_random_time,
                        status = random.choice(status_list),
                        time_slot_id = random.choice(slotid_list),
                        doctor_id = random.choice(doctorid_list),
                        approver_id = random.choice(nurseid_list),
                        patient_id = random.choice(patientid_list),
                        symptoms = random.choice(["fever","dry cough","tiredness","sore throat"])
        )
        db.session.add(appt)
    db.session.commit()

def practice_query():
    pending_appt = Application.query.filter(Application.app_timestamp>datetime.datetime.now(), 
                                            Application.status==StatusEnum.pending)
    print(pending_appt.limit(3).all())


practice_query()
def main():
    # please do not change the following execution order
    print("on it")
    # gen_hospital_data()
    # gen_dept_data()
    # gen_user_data()
    # gen_time_slot()
    # gen_appt()

# main()
    