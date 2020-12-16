# EHR System -- WeCare
Fall 2020 Software Engineering
## Description
The WeCare electronic health record system is an integrated platform for healthcare appointment management, medical record management and workspace for healthcare providers. </br>
We define electronic health record by three parts: </br>
1. basic health information including age, gender, blood type, allergies, medications and chronic conditions.</br>
2. healthcare appointment information.</br>
3. medical records including vital signs, diagnosis, prescriptions and lab reports.</br>
### Patient
Patients can register with their national ID. After registration, patients will have access to our healthcare appointment making and medical record collection services. On our healthcare appointment making platform, patients can search for hospitals, departments and doctors and make appointments with doctors who specialize in your illness. Patients can track the status of their appointments, view past appointments and review their medical records. </br>
### Doctor and Nurse
Healthcare providers (doctors and nurses) need to register with their department ID and license ID.</br>
Doctors have a default homepage showing all the ongoing appointments. They can go into the medical record of the ongoing appointments and add diagnosis, prescriptions and lab report requests. They can press the "finish" button to end an appointment. Doctors also have access to their appointments of the current day, future appointments and past appointments. Doctors can see their schedule in a calendar view and create new time slots and specify the number of available appointments.</br>
Nurses have a default homepage showing all the pending appointment applications in their department. Nurses need to judge from the patient's symptoms to decide whether to approve or reject a pending application. They can review all the applications rejected by them. Nurses also have access to appointments of the current day, ongoing appointments, future appointments and past appointments in their department. They can upload pre-exam results (vital signs) for an unfinished appointment and upload lab reports to fulfill a doctor's lab report request. Nurses can also create new appointments for patients visiting the hospital in person directly.</br>
Doctors and nurses can view the medical record history and basic health information of the patient of the ongoing appointment. Those information can help doctors and nurses make better medical decisions.
## Contributions
| Task | Subtask | Name |
| :---: | :---: | :---: |
| UI design | patient | Zhenming Wang |
|  | doctor | Ren Sheng |
|  | nurse | Jingyi Zhu |
| :---: | :---: | :---: |
| Database design |  | Qing Deng, Jingyi Zhu |
| :---: | :---: | :---: |
| Frontend development | patient | Zhenming Wang |
|  | doctor | Jingyi Zhu, Zhenming Wang |
|  | nurse | Jingyi Zhu |
| :---: | :---: | :---: |
| Backend development |  | Qing Deng, Ren Sheng, Jingyi Zhu |
| :---: | :---: | :---: |
| Testing |  | Qing Deng, Ren Sheng, Jingyi Zhu |
## Run the project
Download this github repository as a folder.</br>
In the terminal, go into the folder.</br>
Make sure you have installed all the dependencies: Flask, Flask_SQLAlchemy (dialect), pymysql (connector), cryptography, flask-login </br>
Run `$python run.py`.
