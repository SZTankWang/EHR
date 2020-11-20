/**
* @author: Jingyi
* @desc HTML modal wrappers
* @method setApp - set application data
* @method setCommets - set comments
* @method setMCID - set medical record
* @method ...
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

class AppFullModal extends AppModal{
  constructor(){
    super();
    this.comments = $("#comments");
  }

  setComments(comments){
    this.comments.text(comments);
  }
}

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
