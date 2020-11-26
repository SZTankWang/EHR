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
    this.state = $("#state option:selected");
    this.diagnosis = $("#diagnosis");
    this.prescriptions = $("#prescriptions");
    this.labReports = $("#labReports");
  }

  setAppStatus(appStatus){
    this.appStatus.text(appStatus);
  }

  setMCID(mcID){
    this.mcID.text(mcID);
  }

  setBodyTemperature(bodyTemperature){
    this.bodyTemperature.val(bodyTemperature);
  }

  setHeartRate(heartRate){
    this.heartRate.val(heartRate);
  }

  setHighBloodPressure(highBloodPressure){
    this.highBloodPressure.val(highBloodPressure);
  }

  setLowBloodPressure(lowBloodPressure){
    this.lowBloodPressure.val(lowBloodPressure);
  }

  setWeight(weight){
    this.weight.val(weight);
  }

  setHeight(height){
    this.height.val(height);
  }

  setState(state){
    var str = "option[value=" + state + "]";
    $("#state " + str).attr('selected','selected');
    this.state = $("#state option:selected");
  }

  setDiagnosis(diagnosis){
    this.diagnosis.text(diagnosis)
  }

  setPrescriptions(prescripitions){
    for (let i=0; i < prescripitions.length; i++) {
      this.prescriptions.append(newPrescriptionCard(i+1, prescripitions[i].id + ": " + prescripitions[i].medicine, prescripitions[i].dose, prescripitions[i].comments));
    };
  }

  setLabReports(labReports){
    for (let i=0; i < labReports.length; i++){
      this.labReports.append(newLabReportCard(i+1, labReports[i].lr_type, labReports[i].id, labReports[i].comments));
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
    sendRequest("nurseViewAppt", "POST", mcData, fillMCData);
  }
}

/**
* @desc page for application and medical record
* @page nurseViewAppt
* @attribute medical record: appStatus, mcID,
* preExam(bodyTemperature, heartRate, bloodPressure),
* diagnosis, precriptions, labReports, labReportTypes
* @method setMCID, setPreExam, setDiagnosis, setPrescriptions, setLabReports
*/
class MCPage extends MCModal{
  constructor(){
    super();
    this.labReportTypes = $("#labReportTypes");
  }

  setLabReportTypes(labReportTypes){
    for (let i=0; i < labReportTypes.length; i++) {
      this.labReportTypes.append(new Option(labReportTypes[i].type, labReportTypes[i].type));
    };
  }

  loadMCInfo(mcID) {
    const mcData = {"mcID": mcID, "type": "True"};
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
        if (res.labReportTypes)
          this.setLabReportTypes(res.labReportTypes);
        if (res.labReports)
          this.setLabReports(res.labReports);
      } else {
        alert(res.ret);
      }
    };
    sendRequest("nurseViewAppt", "POST", mcData, fillMCData);
  }
}
