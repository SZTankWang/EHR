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
* preExam(bodyTemperature, heartRate, highBloodPressure, lowBloodPressure, weight, height, state),
* diagnosis, precriptions, labReports
* @method checkAndSet, setAppStatus, setMCID, (setPreExam), setDiagnosis, setPrescriptions, setLabReports,
loadAppInfo, loadMCInfo
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

  setState(state){
    if (this.state.is("select")) {
      var str = "option[value=" + state + "]";
      $("#state " + str).attr('selected','selected');
      this.state = $("#state option:selected");
    } else {
      this.state.text(state);
    }
  }

  setPreExam(preExam){
    this.checkAndSet(this.bodyTemperature, preExam.bodyTemperature);
    this.checkAndSet(this.heartRate, preExam.heartRate);
    this.checkAndSet(this.highBloodPressure, preExam.highBloodPressure);
    this.checkAndSet(this.lowBloodPressure, preExam.lowBloodPressure);
    this.checkAndSet(this.weight, preExam.weight);
    this.checkAndSet(this.height, preExam.height);
    this.setState(preExam.state)
  }

  setDiagnosis(diagnosis){
    this.diagnosis.text(diagnosis);
  }

  setPrescriptions(prescripitions){
    this.prescriptions.empty();
    for (let i=0; i < prescripitions.length; i++) {
      this.prescriptions.append(newPrescriptionCard(i+1, prescripitions[i].id, prescripitions[i].medicine, prescripitions[i].dose, prescripitions[i].comments));
    };
  }

  setLabReports(labReports){
    this.labReports.empty();
    for (let i=0; i < labReports.length; i++) {
      const path = labReports[i].file_path ? labReports[i].file_path : "";
      this.labReports.append(newLabReportCard(i+1, labReports[i].id, labReports[i].lr_type, labReports[i].doctor_comments, labReports[i].nurse_comments, path));
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
    const mcData = {"mcID": mcID, "type": "0"};
    var fillMCData = (res) => {
      if (res.ret == "0") {
        this.setPreExam(res.preExam);
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
* @attribute labReportTypes, labReportReqs,
patientBasicInfo(patientID, age, gender, bloodType, allergies, chronics, medications)
* @method loadPatientInfo, setLbaReportAndReqs, setLabReportTypes, loadMCInfo(override)
*/
class MCPage extends MCModal{
  constructor(){
    super();
    this.labReportTypes = $("#labReportTypeInput");
    this.labReportReqs = $("#labReportReqs");
    this.patientID = $("#patientID").val();
    this.age = $("#age");
    this.gender = $("#gender");
    this.bloodType = $("#bloodType");
    this.allergies = $("#allergies");
    this.chronics = $("#chronics");
    this.medications = $("#medications");
  }

  setLabReportAndReqs(labReportAndReqs){
    this.labReports.empty();
    this.labReportReqs.empty();
    for (let i=0; i < labReportAndReqs.length; i++) {
      const path = labReportAndReqs[i].file_path ? labReportAndReqs[i].file_path : "";
      if (!path) {
        this.labReportReqs.append(newLabReportReqCard(i+1, labReportAndReqs[i].id, labReportAndReqs[i].lr_type, labReportAndReqs[i].doctor_comments));
      } else {
        this.labReports.append(newLabReportCard(i+1, labReportAndReqs[i].id, labReportAndReqs[i].lr_type, labReportAndReqs[i].doctor_comments, labReportAndReqs[i].nurse_comments, path));
      }
    }
  }

  setLabReportTypes(labReportTypes){
    for (let i=0; i < labReportTypes.length; i++) {
      this.labReportTypes.append(new Option(labReportTypes[i].type, labReportTypes[i].type));
    };
  }

  loadPatientInfo(patientID) {
    var fillInfoData = (res) => {
      this.age.text(res.age);
      this.gender.text(res.gender);
      this.bloodType.text(res.bloodType);
      this.allergies.text(res.allergies);
      this.chronics.text(res.chronics);
      this.medications.text(res.medications);
    };
    sendRequest("getPatientInfo", "POST", {"patientID": patientID}, fillInfoData);
  }

  loadMCInfo(mcID, route, type) {
    const mcData = {"mcID": mcID, "type": type};
    var fillMCData = (res) => {
      if (res.ret == "0") {
        this.setPreExam(res.preExam);
        this.setDiagnosis(res.diagnosis);
        if (res.prescriptions)
          this.setPrescriptions(res.prescriptions);
        if (type) {
          if (res.labReportTypes)
            this.setLabReportTypes(res.labReportTypes);
          if (res.labReports)
            this.setLabReports(res.labReports);
        } else {
          if (res.labReports)
            this.setLabReportAndReqs(res.labReports);
        }
      } else {
        alert(res.ret);
      }
    };
    sendRequest(route, "POST", mcData, fillMCData);
  }
}
