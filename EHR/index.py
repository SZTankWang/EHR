from flask import Flask
from flask import render_template,request
app = Flask(__name__)

@app.route('/')
def helloWorld():
	return render_template('index.html')

@app.route('/WeCare/homepage')
def WeCare():
	return render_template('WeCare.html')

@app.route('/WeCare')
def loginForm():
	return render_template('login.html')

# @app.route('/WeCare/register')
# def registerForm():
# 	return render_template('register.html')

@app.route('/WeCare/choice')
def choice():
	return render_template('choice.html')

@app.route('/WeCare/register')
def handleRegister():
	registerType = request.args.get('register-role')
	print(registerType)
	return "success"

@app.route('/WeCare/login')
def handleLogin():
	# registerType = request.args.get('register-role')
	# print(registerType)
	return "success"

@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/loginTemplate')
def loginTemplate():
	return render_template('temp_login.html')

@app.route('/hospital')
def hospitalTemplate():
	return render_template('hospitalListPage.html')

@app.route('/hospitalData')
def hopitalData():
	print(request.args['currPage'])
	print(request.args['pageSize'])
	return 'OK'


@app.route('/viewDoctor')
def viewDoctor():
	return render_template('doctorPage.html')

@app.route('/patientDepartment')
def patient():
	return render_template('/newDepartmentPage.html')

if __name__ == '__main__':
	app.run(debug=True)    
