import json

def add_hospital(client, name, phone, address, description):
    data = dict(name=name, phone=phone, address=address, description=description)
    return client.post('/addHospital', data=data, follow_redirects=False)

def add_department(client, hospital_id, name, phone, description):
    data = dict(hospitalID=hospital_id, name=name, phone=phone, description=description)
    return client.post('/addDepartment', data=data, follow_redirects=False)

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
    rv = add_hospital(client, "1", "1", "1", "1")
    print(rv.data)
    assert json.loads(rv.data)["ret"] == 0

def test_add_department(client):
    rv = add_department(client, "1", "1", "1", "1")
    print(rv.data)
    assert json.loads(rv.data)["ret"] == 0

def test_register(client):
    rv = register(client, "w", "w", "doctor", "w", 'w', "w", "w", "1")
    print(rv.data)
    assert json.loads(rv.data)["ret"] == 0

# def test_login_logout(client):
#     """Make sure login and logout works."""
#
#     rv = login(client, "w", "w")
#     res = json.loads(rv.data)
#     assert res["ret"] == 0 and res["id"] == "w" and res["role"] == "doctor"
#
#     rv = logout(client)
#     assert rv.data
#
#     rv = login(client, "w" + 'x', "w")
#     assert json.loads(rv.data)["ret"] == 'Unregistered user'
#
#     rv = login(client, "w", "w" + 'x')
#     assert json.loads(rv.data)["ret"] == 'Incorrect password'
