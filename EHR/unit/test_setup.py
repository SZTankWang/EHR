import json

def add_hospital(client, name, phone, address, description):
    data = dict(name=name, phone=phone, address=address, description=description)
    return client.post('/addHospital', data=data, follow_redirects=False)

def add_hospital_exception(client, name, phone, address, description):
    data = dict(name=name, phone=phone, address=address, description=description)
    return client.post('/addHospital', data=data, follow_redirects=True)

def add_department(client, hospital_id, title, phone, description):
    data = dict(hospitalID=hospital_id, title=title, phone=phone, description=description)
    return client.post('/addDepartment', data=data, follow_redirects=False)

def add_department_exception(client, hospital_id, title, phone, description):
    data = dict(hospitalID=hospital_id, title=title, phone=phone, description=description)
    return client.post('/addDepartment', data=data, follow_redirects=True)

def add_lab_report_type(client, type, desc):
    data = dict(type=type, description=desc)
    return client.post('/addLabReportType', data=data, follow_redirects=False)

def register(client, id, password, role, first_name, last_name, phone, email, department):
    data = dict(
        id=id,
        password=password,
        role=role,
        firstName=first_name,
        lastName=last_name,
        phone=phone,
        email=email,
        department = department
    )
    return client.post('/register', data=data, follow_redirects=False)

def login(client, id, password):
    return client.post('/login', data=dict(
        id=id,
        password=password
    ), follow_redirects=False)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_add_hospital(client):
    login(client, "0", "0")
    rv = add_hospital(client, "1", "1", "1", "1")
    assert json.loads(rv.data)["ret"] == 0

    login(client, "d", "d")
    rv = add_hospital_exception(client, "2", "2", "2", "2")

def test_add_department(client):
    login(client, "0", "0")
    rv = add_department(client, "1", "1", "1", "1")
    assert json.loads(rv.data)["ret"] == 0

    login(client, "d", "d")
    rv = add_department_exception(client, "1", "2", "2", "2")

def test_add_lab_report_type(client):
    login(client, "0", "0")
    rv = add_lab_report_type(client, "a", "a")
    assert json.loads(rv.data)["ret"] == 0

    rv = add_lab_report_type(client, "a", "a")
    assert json.loads(rv.data)["ret"] == "Duplicate"

def test_register(client):
    rv = register(client, "n1", "n1", "nurse", "n1", 'n1', "n1", "n1", "1")
    assert json.loads(rv.data)["ret"] == 0

    rv = register(client, "w", "m", "doctor", "m", 'm', "w", "w", "1")
    res = json.loads(rv.data)
    assert res["ret"] == 1 and res['message'] == 'You already registered!'

def test_login_logout(client):
    """Make sure login and logout works."""

    rv = login(client, "n", "n")
    res = json.loads(rv.data)
    assert res["ret"] == 0 and res["id"] == "n" and res["role"] == "nurse"

    rv = logout(client)
    assert rv.data

    rv = login(client, "w" + 'x', "w")
    res = json.loads(rv.data)
    assert res["ret"] == 1 and res["message"] == 'Unregistered user'

    rv = login(client, "w", "w" + 'x')
    res = json.loads(rv.data)
    assert res["ret"] == 1 and res["message"] == 'Incorrect password'
