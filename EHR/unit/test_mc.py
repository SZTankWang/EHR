import json

def login(client, id, password):
    return client.post('/login', data=dict(
        id=id,
        password=password
    ), follow_redirects=False)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def viewAppt(client, route, mcID, type):
    data = dict(mcID=mcID, type=type)
    return client.post(route, data=data, follow_redirects=True)

def makeAppt(client, route, symptom, slotID, doctorID):
    data = dict(symptom = symptom, slotID = slotID, doctorID = doctorID)
    return client.post(route, data=data, follow_redirects=False)

def getslots(client, route):
    return client.get(route,follow_redirects=False)

def addprescrip(client,route,mcID,medicine,dose,comments):
    data = dict(mcID=mcID,medicine=medicine,dose=dose,comments=comments)
    return client.post(route,data = data, follow_redirects=False)

def getprescrip(client,route,mcID):
    data = dict(mcID=mcID)
    return client.post(route,data=data,follow_redirects=False)

def getlabreport(client,route,mcID):
    data = dict(mcID = mcID)
    return client.post(route,data=data,follow_redirects=False)



#-------------------------------test-------------------------------
def test_doctorAddPrescrip(client):
    login(client,"d","d")
    rv = addprescrip(client,"/doctorAddPrescrip","1","Aspirin","2","more hot water")
    res = json.loads(rv.data)
    assert res["ret"] == 0
    logout(client)

def test_doctorGetPrescrip(client):
    login(client,"d","d")
    rv = getprescrip(client,"/doctorGetPrescrip","1")
    res = json.loads(rv.data)
    assert res["ret"] == 0

    rv = getprescrip(client,"/doctorGetPrescrip","a")
    res = json.loads(rv.data)
    assert res["ret"] == 'Medical Record Not Found!'
    logout(client)

def test_getLabReport(client):
    login(client,"n","n")
    rv = getlabreport(client,"/nurseGetLabReports","1")
    res = json.loads(rv.data)
    assert res["ret"] == 0

    rv = getlabreport(client,"/nurseGetLabReports","a")
    res = json.loads(rv.data)
    assert res["ret"] == 'Medical Record Not Found!'
    logout(client)

    login(client,"d","d")
    rv = getlabreport(client,"/doctorGetLabReports","1")
    res = json.loads(rv.data)
    assert res["ret"] == 0

    rv = getlabreport(client,"/doctorGetLabReports","a")
    res = json.loads(rv.data)
    assert res["ret"] == 'Medical Record Not Found!'
    logout(client)

def test_doctorGetSlots(client):
    login(client,"d","d")

    rv = getslots(client, "/doctorGetSlots")
    res = json.loads(rv.data)
    assert res["ret"] == 0
    logout(client)

def test_patientMakeAppt(client):
    login(client,"p","p")

    rv = makeAppt(client, "/makeAppt", "test", "3", "d")
    res = json.loads(rv.data)
    assert res["ret"] == 0

    rv = makeAppt(client, "/makeAppt", "test", "2", "d")
    res = json.loads(rv.data)
    assert res["ret"] == 1 and res['message']=="no available slots!"
    logout(client)

def test_nurseViewAppt(client):
    login(client, "n", "n")

    # get a medical record
    rv = viewAppt(client, "/nurseViewAppt", "1", "0")
    res = json.loads(rv.data)
    assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res

    # get a medical record without lab report types but not allowed
    rv = viewAppt(client, "/nurseViewAppt", "1", "1")
    res = json.loads(rv.data)
    assert res["ret"] == "Access to lab report types not granted"

    # get a non-existent medical record
    rv = viewAppt(client, "/nurseViewAppt", "a", "0")
    res = json.loads(rv.data)
    assert res["ret"] == "Medical Record Not Found!"
    logout(client)


def test_doctorViewAppt(client):
    login(client, "d", "d")

    # get a medical record without lab report types
    rv = viewAppt(client, "/doctorViewAppt", "1", "0")
    res = json.loads(rv.data)
    assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res

    # get a medical record without lab report types
    rv = viewAppt(client, "/doctorViewAppt", "1", "1")
    res = json.loads(rv.data)
    assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res
    assert "labReportTypes" in res

    # get a non-existent medical record
    rv = viewAppt(client, "/doctorViewAppt", "a", "1")
    res = json.loads(rv.data)
    assert res["ret"] == "Medical Record Not Found!"
    logout(client)


def test_doctorNurseViewAppt(client):
    # get a medical record as doctor
    login(client, "d", "d")
    rv = viewAppt(client, "/doctorNurseViewAppt", "1", "0")
    res = json.loads(rv.data)
    assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res
    logout(client)
    # get a medical record as nurse
    login(client, "n", "n")
    rv = viewAppt(client, "/doctorNurseViewAppt", "1", "0")
    res = json.loads(rv.data)
    assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res
    logout(client)

def test_viewAppt_notAllowed(client):
    login(client, "p", "p")

    # the route can't be used by patient
    rv = viewAppt(client, "/nurseViewAppt", "1", "0")
    assert rv.data

    rv = viewAppt(client, "/doctorViewAppt", "1", "1")
    assert rv.data

    rv = viewAppt(client, "/doctorNurseViewAppt", "1", "0")
    assert rv.data
    logout(client)
