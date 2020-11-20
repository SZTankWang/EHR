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
* @desc modal for application
* @attribute medical record: mcID,
* preExam(bodyTemperature, pulseRate, bloodPressure),
* diagnosis, precriptions, labReports
* @method setMCID, setPreExam, setDiagnosis, setPrescriptions, setLabReports
*/
class MCModal extends AppFullModal{
  constructor(){
    super();
    this.mcID = $("#mcID");
    this.bodyTemperature = $("#bodyTemperature");
    this.pulseRate = $("#pulseRate");
    this.bloodPressure = $("#bloodPressure");
    this.diagnosis = $("#diagnosis");
  }

  setMCID(mcID){
    this.mcID.text(mcID);
  }

  setPreExam(data){
  }

  setDiagnosis(data){
  }

  setPrescriptions(data){
  }

  setLabReports(data){
  }
}
