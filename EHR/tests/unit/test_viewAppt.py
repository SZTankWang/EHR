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
    return client.post(route, data=data, follow_redirects=False)

#-------------------------------test-------------------------------

def test_nurseViewAppt(client):
    login(client, "n", "n")

    rv = viewAppt(client, "/nurseViewAppt", "1", "0")
    res = json.loads(rv.data)
    assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res

    rv = viewAppt(client, "/nurseViewAppt", "1", "1")
    res = json.loads(rv.data)
    assert res["ret"] == "Access to lab report types not granted"

    rv = viewAppt(client, "/nurseViewAppt", "a", "0")
    res = json.loads(rv.data)
    assert res["ret"] == "Medical Record Not Found!"


def test_doctorViewAppt(client):
    login(client, "w", "w")

    rv = viewAppt(client, "/doctorViewAppt", "1", "0")
    res = json.loads(rv.data)
    assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res

    rv = viewAppt(client, "/doctorViewAppt", "1", "1")
    res = json.loads(rv.data)
    assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res
    assert "labReportTypes" in res

    rv = viewAppt(client, "/doctorViewAppt", "a", "1")
    res = json.loads(rv.data)
    assert res["ret"] == "Medical Record Not Found!"


def test_doctorNurseViewAppt(client):
    login(client, "w", "w")

    rv = viewAppt(client, "/doctorNurseViewAppt", "1", "0")
    res = json.loads(rv.data)
    assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res

    login(client, "n", "n")
    rv = viewAppt(client, "/doctorNurseViewAppt", "1", "0")
    res = json.loads(rv.data)
    assert res["ret"] == "0" and "preExam" in res and "diagnosis" in res and "prescriptions" in res and "labReports" in res


def test_viewAppt_notAllowed(client):
    login(client, "p", "p")

    rv = viewAppt(client, "/nurseViewAppt", "1", "0")
    res = json.loads(rv.data)
    assert res["ret"] == "Privilege not granted"

    rv = viewAppt(client, "/doctorViewAppt", "1", "1")
    res = json.loads(rv.data)
    assert res["ret"] == "Privilege not granted"

    rv = viewAppt(client, "/doctorNurseViewAppt", "1", "0")
    res = json.loads(rv.data)
    assert res["ret"] == "Privilege not granted"
