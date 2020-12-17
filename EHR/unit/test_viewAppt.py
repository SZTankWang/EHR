# import json
#
# def login(client, id, password):
#     return client.post('/login', data=dict(
#         id=id,
#         password=password
#     ), follow_redirects=False)
#
# def logout(client):
#     return client.get('/logout', follow_redirects=True)
#
# def viewAppt(client, route, mcID, type):
#     data = dict(mcID=mcID, type=type)
#     return client.post(route, data=data, follow_redirects=False)
#
# #-------------------------------test-------------------------------
#
# def test_nurseViewAppt(client):
#     login(client, "n", "n")
#
#     # get a medical record
#     rv = viewAppt(client, "/nurseViewAppt", "1", "0")
#     res = json.loads(rv.data)
#     assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res
#
#     # get a medical record without lab report types but not allowed
#     rv = viewAppt(client, "/nurseViewAppt", "1", "1")
#     res = json.loads(rv.data)
#     assert res["ret"] == "Access to lab report types not granted"
#
#     # get a non-existent medical record
#     rv = viewAppt(client, "/nurseViewAppt", "a", "0")
#     res = json.loads(rv.data)
#     assert res["ret"] == "Medical Record Not Found!"
#
#
# def test_doctorViewAppt(client):
#     login(client, "w", "w")
#
#     # get a medical record without lab report types
#     rv = viewAppt(client, "/doctorViewAppt", "1", "0")
#     res = json.loads(rv.data)
#     assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res
#
#     # get a medical record without lab report types
#     rv = viewAppt(client, "/doctorViewAppt", "1", "1")
#     res = json.loads(rv.data)
#     assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res
#     assert "labReportTypes" in res
#
#     # get a non-existent medical record
#     rv = viewAppt(client, "/doctorViewAppt", "a", "1")
#     res = json.loads(rv.data)
#     assert res["ret"] == "Medical Record Not Found!"
#
#
# def test_doctorNurseViewAppt(client):
#     # get a medical record as doctor
#     login(client, "w", "w")
#     rv = viewAppt(client, "/doctorNurseViewAppt", "1", "0")
#     res = json.loads(rv.data)
#     assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res
#
#     # get a medical record as nurse
#     login(client, "n", "n")
#     rv = viewAppt(client, "/doctorNurseViewAppt", "1", "0")
#     res = json.loads(rv.data)
#     assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res
#
#
# def test_viewAppt_notAllowed(client):
#     login(client, "p", "p")
#
#     # the route can't be used by patient
#     rv = viewAppt(client, "/nurseViewAppt", "1", "0")
#     res = json.loads(rv.data)
#     assert res["ret"] == "Privilege not granted"
#
#     rv = viewAppt(client, "/doctorViewAppt", "1", "1")
#     res = json.loads(rv.data)
#     assert res["ret"] == "Privilege not granted"
#
#     rv = viewAppt(client, "/doctorNurseViewAppt", "1", "0")
#     res = json.loads(rv.data)
#     assert res["ret"] == "Privilege not granted"
