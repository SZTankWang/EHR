/**
* @author Jingyi Zhu
* @page doctorViewAppt.html
* @import modal.js, util.js, apptAndMC.js
*/

/**
* @global instance of MCPage
*/
var myPage;

//-------------------------document loaded---------------------------
$(document).ready(function() {
    // initialize instance
    myPage = new MCPage();
    // request and fill in app status and comments
    const appID = myPage.appID.text();
    myPage.loadAppInfo(appID);
    // request and fill in patient basic info
    const patientID = myPage.patientID;
    myPage.loadPatientInfo(patientID);
    // request and fill in medical record data
    const mcID = myPage.mcID.text();
    myPage.loadMCInfo(mcID, "doctorViewAppt", true);
});


// ---------------------capture user action--------------------------
// edit diagnosis
$("#diagnosisForm").on("submit", editDiagnosis);

// add prescription
$("#prescriptionForm").on("submit", addPrescription);

// upload a lab report
$("#labReportForm").on("submit", requestLabReport);


// --------------------------event handlers----------------------------
/**
* @desc finish appointment
* @param {event} event - click
*/
function finish(event){
  var appID = myPage.appID.text();
  var data = {'appID': appID};

  var refresh = (res) => {refreshOnSuccess(res)};
  sendRequest("doctorFinishAppt", "POST", data, refresh);
}

/**
* @desc edit diagnosis
* @param {event} event - submit
* @this event target element - diagnosis form
*/
function editDiagnosis(event){
  event.preventDefault();
  var mcID = myPage.mcID.text();
  var data = jsonify($(this).serializeArray());
  data.mcID = mcID;

  var callBack = function(res) {
    if (res.ret) {
      alert(res.ret);
    }
  }
  sendRequest("doctorEditDiag", "POST", data, callBack);
}


/**
* @desc submit prescription
* @param {event} event - submit
* @this event target element - prescription form
*/
function addPrescription(event){
  event.preventDefault();
  var mcID = myPage.mcID.text();
  var data = jsonify($(this).serializeArray());
  data.mcID = mcID;

  // var refresh = (res) => {refreshOnSuccess(res)};
  var refresh = (res) => {
    if (!res.ret) {
      sendRequest("doctorGetPrescrip", "POST", {"mcID": mcID},
      (res) => {
        if (!res.ret) {
          myPage.setPrescriptions(res.prescriptions);
          $("#medicine").val(null);
          $("#dose").val(null);
          $("#comments").val(null);
        } else {
          alert(res.ret);
        }
      });
    }
  };
  sendRequest("doctorAddPrescrip", "POST", data, refresh);
}

/**
* @desc request a lab report to be uploaded after examination
* @param {event} event - submit
* @this event target element - labReport form
*/
function requestLabReport(event){
  event.preventDefault();
  var mcID = myPage.mcID.text();
  var data = jsonify($(this).serializeArray());
  data.mcID = mcID;
  var callBack = function(res) {
    if (!res.ret) {
      $("#labReportTypeInput option:selected").prop("selected", false);
      $("#commentsInput").val(null);
      sendRequest("doctorGetLabReports", "POST", {"mcID": mcID},
      (res) => {
        if (!res.ret) {
          myPage.setLabReports(res.labReports);
        } else {
          alert(res.ret);
        }
      });
    } else {
      alert(res.ret);
    }
  }
  sendRequest("doctorReqLabReport", "POST", data, callBack);
}

// refresh page if submission is successful
function refreshOnSuccess(res){
   if (res.ret == "0") {
     goToPage("doctorGoViewAppt/" + myPage.appID.text(), 0)
   }
 }
