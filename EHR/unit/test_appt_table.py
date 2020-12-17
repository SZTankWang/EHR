import json
import datetime
from EHR.Controller import control_helper as helper
from .test_setup import login, logout

def postApptsData(client, route, start, end):
    data = dict(startDate=start, endDate=end)
    response = client.post(route, data=data, follow_redirects=False)
    if 300 <= response.status_code < 400:
        response = client.get(response.headers['Location'], headers={
            "Referer": 'http://localhost:5000/loadHomePage'
        })
    return response

def getApptsData(client, route):
    response = client.get(route, follow_redirects=False)
    if 300 <= response.status_code < 400:
        response = client.get(response.headers['Location'], headers={
            "Referer": 'http://localhost:5000/loadHomePage'
        })
    return response

def test_apptRole(client):
    login(client, "d", "d")
    rv = getApptsData(client, "/doctorAllAppt")
    logout(client)

    login(client, "n1", "n1")
    rv = getApptsData(client, "/doctorAllAppt")
    logout(client)

    login(client, "p", "p")
    rv = getApptsData(client, "/doctorAllAppt")
    logout(client)

    login(client, "n1", "n1")
    rv = getApptsData(client, "/nurseAllAppt")
    logout(client)

    login(client, "d", "d")
    rv = getApptsData(client, "/nurseAllAppt")
    logout(client)

    login(client, "p", "p")
    rv = getApptsData(client, "/nurseAllAppt")
    logout(client)


def test_todayAppt(client):
    today = datetime.datetime.today().strftime(helper.DATE_FORMAT)

    login(client, "d", "d")
    rv = getApptsData(client, "/doctorTodayAppt")
    if rv.status_code == 200:
        res = json.loads(rv.data)
        assert res==[] or ("appID" in res[0] and res[0]["date"] == today and "time" in res[0] and "nurse" in res[0] and "patient" in res[0] and "symptoms" in res[0])
    logout(client)

    login(client, "n1", "n1")
    rv = getApptsData(client, "/nurseTodayAppt")
    if rv.status_code == 200:
        res = json.loads(rv.data)
        assert res==[] or ("appID" in res[0] and res[0]["date"] == today and "time" in res[0] and "doctor" in res[0] and "patient" in res[0] and "symptoms" in res[0])
    logout(client)


def test_ongoingAppt(client):
    today = datetime.datetime.today().strftime(helper.DATE_FORMAT)
    now = datetime.datetime.now().strftime(helper.TIME_FORMAT)

    login(client, "d", "d")
    rv = getApptsData(client, "/doctorOnGoingAppt")
    if rv.status_code == 200:
        res = json.loads(rv.data)
        assert res==[] or ("appID" in res[0] and res[0]["date"] == today and res[0]["now"] == now and "nurse" in res[0] and "patient" in res[0] and "symptoms" in res[0])
    logout(client)

    login(client, "n1", "n1")
    rv = getApptsData(client, "/nurseOnGoingAppt")
    if rv.status_code == 200:
        res = json.loads(rv.data)
        assert res==[] or ("appID" in res[0] and res[0]["date"] == today and res[0]["now"] == now and "doctor" in res[0] and "patient" in res[0] and "symptoms" in res[0])
    logout(client)


def test_apptDirection(client):
    today = datetime.datetime.today()

    login(client, "n1", "n1")
    rv = getApptsData(client, "/nursePendingApp")
    if rv.status_code == 200:
        res = json.loads(rv.data)
        assert res==[] or ("appID" in res[0] and datetime.datetime.strptime(res[0]["date"], helper.DATE_FORMAT) >= today and "time" in res[0] and "doctor" in res[0] and "patient" in res[0] and "symptoms" in res[0])
    logout(client)

    login(client, "n1", "n1")
    rv = postApptsData(client, "/nursePastAppt", "", datetime.datetime.strftime(datetime.datetime.now(), helper.DATE_FORMAT))
    if rv.status_code == 200:
        res = json.loads(rv.data)
        assert res==[] or ("appID" in res[0] and datetime.datetime.strptime(res[0]["date"], helper.DATE_FORMAT) <= today and "time" in res[0] and "doctor" in res[0] and "patient" in res[0] and "symptoms" in res[0])
    logout(client)

    login(client, "n1", "n1")
    rv = postApptsData(client, "/nurseFutureAppt", datetime.datetime.strftime(datetime.datetime.now(), helper.DATE_FORMAT), "")
    if rv.status_code == 200:
        res = json.loads(rv.data)
        assert res==[] or ("appID" in res[0] and datetime.datetime.strptime(res[0]["date"], helper.DATE_FORMAT) >= today and "time" in res[0] and "doctor" in res[0] and "patient" in res[0] and "symptoms" in res[0])
    logout(client)

    login(client, "d", "d")
    rv = getApptsData(client, "/doctorPastAppt")
    if rv.status_code == 200:
        res = json.loads(rv.data)
        assert res==[] or ("appID" in res[0] and datetime.datetime.strptime(res[0]["date"], helper.DATE_FORMAT) <= today and "time" in res[0] and "nurse" in res[0] and "patient" in res[0] and "symptoms" in res[0])
    logout(client)

    login(client, "d", "d")
    rv = getApptsData(client, "/doctorFutureAppt")
    if rv.status_code == 200:
        res = json.loads(rv.data)
        assert res==[] or ("appID" in res[0] and datetime.datetime.strptime(res[0]["date"], helper.DATE_FORMAT) >= today and "time" in res[0] and "nurse" in res[0] and "patient" in res[0] and "symptoms" in res[0])
    logout(client)
