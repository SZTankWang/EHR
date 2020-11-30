/**
* @author Jingyi Zhu
* @desc HTML modal wrappers
*/

/**
* @desc modal for pending application
* @page nursePendingApp
* @attribute basic info: appID, date, time, doctor, patient, symptoms
* @method setApp - set basic info
*/
class AppModal {
  constructor(){
    this.myself = $("#application");
    this.appID = $("#appID");
    this.date = $("#date");
    this.time = $("#time");
    this.doctor = $("#doctor");
    this.patient = $("#patient");
    this.symptoms = $("#symptoms");
  }

  setApp(data){
    this.appID.text(data['appID']);
    this.date.text(data['date']);
    this.time.text(data['time']);
    this.doctor.text(data['doctor']);
    this.patient.text(data['patient']);
    this.symptoms.text(data['symptoms']);
  }

  show(){
    this.myself.modal('show');
  }

  hide(){
    this.myself.modal('hide');
  }
}

/**
* @desc modal for application
* @page nurseRejectedApp
* @attribute comments
* @method setComments
*/
class AppFullModal extends AppModal{
  constructor(){
    super();
    this.comments = $("#comments");
  }

  setComments(comments){
    this.comments.text(comments);
  }
}

/**
* @desc modal for application and medical record
* @page nurseViewMC
* @attribute medical record: appStatus, mcID,
* preExam(bodyTemperature, heartRate, bloodPressure),
* diagnosis, precriptions, labReports
* @method setMCID, setPreExam, setDiagnosis, setPrescriptions, setLabReports
*/
class MCModal extends AppFullModal{
  constructor(){
    super();
    this.appStatus = $("#appStatus");
    this.mcID = $("#mcID");
    this.bodyTemperature = $("#bodyTemperature");
    this.heartRate = $("#heartRate");
    this.highBloodPressure = $("#highBloodPressure");
    this.lowBloodPressure = $("#lowBloodPressure");
    this.weight = $("#weight");
    this.height = $("#height");
    this.state = $("#state");
    this.diagnosis = $("#diagnosis");
    this.prescriptions = $("#prescriptions");
    this.labReports = $("#labReports");
  }

  checkAndSet(element, data) {
    if (element.is("input")) {
      // if (element != "") {
      //   element.attr("disabled", true);
      // }
      element.val(data);
    } else {
      element.text(data);
    }
  }

  setAppStatus(appStatus){
    this.appStatus.text(appStatus);
  }

  setMCID(mcID){
    this.mcID.text(mcID);
  }

  setBodyTemperature(bodyTemperature){
    this.checkAndSet(this.bodyTemperature, bodyTemperature);
  }

  setHeartRate(heartRate){
    this.checkAndSet(this.heartRate, heartRate);
  }

  setHighBloodPressure(highBloodPressure){
    this.checkAndSet(this.highBloodPressure, highBloodPressure);
  }

  setLowBloodPressure(lowBloodPressure){
    this.checkAndSet(this.lowBloodPressure, lowBloodPressure);
  }

  setWeight(weight){
    this.checkAndSet(this.weight, weight);
  }

  setHeight(height){
    this.checkAndSet(this.height, height);
  }

  setState(state){
    if (this.state.is("select")) {
      var str = "option[value=" + state + "]";
      $("#state " + str).attr('selected','selected');
      this.state = $("#state option:selected");
    } else {
      this.state.text(state);
    }
  }

  setDiagnosis(diagnosis){
    this.diagnosis.text(diagnosis);
  }

  setPrescriptions(prescripitions){
    this.prescriptions.empty();
    for (let i=0; i < prescripitions.length; i++) {
      this.prescriptions.append(newPrescriptionCard(i+1, prescripitions[i].id + ": " + prescripitions[i].medicine, prescripitions[i].dose, prescripitions[i].comments));
    };
  }

  setLabReports(labReports){
    this.labReports.empty();
    for (let i=0; i < labReports.length; i++) {
      this.labReports.append(newLabReportCard(i+1, labReports[i].lr_type, labReports[i].id, labReports[i].comments, labReports[i].file_path));
    };
  }

  loadAppInfo(appID){
    const appData = {"appID": appID};
    var fillAppData = (res) => {
      this.setAppStatus(res.status);
      this.setComments(res.comments);
    };
    sendRequest("getComments", "POST", appData, fillAppData);
  }

  loadMCInfo(mcID) {
    const mcData = {"mcID": mcID, "type": "False"};
    var fillMCData = (res) => {
      if (res.ret == "0") {
        this.setBodyTemperature(res.preExam.bodyTemperature);
        this.setHeartRate(res.preExam.heartRate);
        this.setHighBloodPressure(res.preExam.highBloodPressure);
        this.setLowBloodPressure(res.preExam.lowBloodPressure);
        this.setWeight(res.preExam.weight);
        this.setHeight(res.preExam.height);
        this.setState(res.preExam.state);
        this.setDiagnosis(res.diagnosis);
        if (res.prescriptions)
          this.setPrescriptions(res.prescriptions);
        if (res.labReports)
          this.setLabReports(res.labReports);
      } else {
        alert(res.ret);
      }
    };
    sendRequest("doctorNurseViewAppt", "POST", mcData, fillMCData);
  }
}

/**
* @desc page for application and medical record
* @page doctorNurseViewAppt
* @attribute medical record: appStatus, mcID,
* preExam(bodyTemperature, heartRate, bloodPressure),
* diagnosis, precriptions, labReports, labReportTypes
* @method setMCID, setPreExam, setDiagnosis, setPrescriptions, setLabReports
*/
class MCPage extends MCModal{
  constructor(){
    super();
    this.labReportTypes = $("#labReportTypeInput");
    this.labReportReqs = $("#labReportReqs");
  }

  setLabReportReqs(labReportReqs){
    this.labReportReqs.empty();
    for (let i=0; i < labReportReqs.length; i++) {
      this.labReportReqs.append(newLabReportReqCard(i+1, labReportReqs[i].id, labReportReqs[i].lr_type, labReportReqs[i].comments));
    }
  }

  setLabReportAndReqs(labReportAndReqs){
    this.labReports.empty();
    this.labReportReqs.empty();
    for (let i=0; i < labReportAndReqs.length; i++) {
      if (labReportAndReqs[i].file_path) {
        console.log(labReportAndReqs[i].file_path);
        this.labReportReqs.append(newLabReportReqCard(i+1, labReportReqs[i].id, labReportReqs[i].lr_type, labReportReqs[i].comments));
      } else {
        this.labReports.append(newLabReportCard(i+1, labReportAndReqs[i].lr_type, labReportAndReqs[i].id, labReportAndReqs[i].comments, labReportAndReqs[i].file_path));
      }
    }
  }

  setLabReportTypes(labReportTypes){
    for (let i=0; i < labReportTypes.length; i++) {
      this.labReportTypes.append(new Option(labReportTypes[i].type, labReportTypes[i].type));
    };
  }

  loadMCInfo(mcID, route, type, req) {
    const mcData = {"mcID": mcID, "type": type, "req": req};
    var fillMCData = (res) => {
      if (res.ret == "0") {
        this.setBodyTemperature(res.preExam.bodyTemperature);
        this.setHeartRate(res.preExam.heartRate);
        this.setHighBloodPressure(res.preExam.highBloodPressure);
        this.setLowBloodPressure(res.preExam.lowBloodPressure);
        this.setWeight(res.preExam.weight);
        this.setHeight(res.preExam.height);
        this.setState(res.preExam.state);
        this.setDiagnosis(res.diagnosis);
        if (res.prescriptions)
          this.setPrescriptions(res.prescriptions);
        if (type) {
          if (res.labReportTypes)
            this.setLabReportTypes(res.labReportTypes);
          if (res.labReports)
            this.setLabReports(res.labReports);
        } else {
          if (res.labReportReqs)
            this.setLabReportReqs(res.labReportReqs);
          if (res.labReportAndReqs)
            this.setLabReportAndReqs(res.labReportAndReqs);
        }
      } else {
        alert(res.ret);
      }
    };
    sendRequest(route, "POST", mcData, fillMCData);
  }
}
