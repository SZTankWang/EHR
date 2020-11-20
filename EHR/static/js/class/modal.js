/**
* @author Jingyi Zhu
* @desc HTML modal wrappers
* @method setApp - set application data
* @method setCommets - set comments
* @method setMCID - set medical record
* @method ...
*/

/**
* @desc modal for pending application
* @page nursePendingApp
* @attribute basic info: appID, date, time, doctor, patient, symptoms
* @method setApp - set basic info
*/
class AppModal {
  constructor(){
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
* @page nurseViewAppt
* @attribute medical record: appStatus, mcID,
* preExam(bodyTemperature, pulseRate, bloodPressure),
* diagnosis, precriptions, labReports
* @method setMCID, setPreExam, setDiagnosis, setPrescriptions, setLabReports
*/
class MCModal extends AppFullModal{
  constructor(){
    super();
    this.appStatus = $("#appStatus");
    this.mcID = $("#mcID");
    this.bodyTemperature = $("#bodyTemperature");
    this.pulseRate = $("#pulseRate");
    this.bloodPressure = $("#bloodPressure");
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
    this.bodyTemperature.text(bodyTemperature);
  }

  setPulseRate(pulseRate){
    this.pulseRate.text(pulseRate);
  }

  setBloodPressure(bloodPressure){
    this.bloodPressure.text(bloodPressure);
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
}

/**
* @desc page for application and medical record
* @page nurseViewMC
* @attribute medical record: appStatus, mcID,
* preExam(bodyTemperature, pulseRate, bloodPressure),
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
      this.labReportTypes.append(new Option(labReportTypes[i].typeName, labReportTypes[i].typeID));
    };
  }
}
