/**
* @author Jingyi Zhu
* @page nurseViewAppt.html
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
    myPage.loadMCInfo(mcID, "nurseViewAppt", false);
});


// ---------------------capture user action--------------------------
// edit preExam data
$("#PreExamForm").on("submit", editPreExam);

// --------------------------event handlers----------------------------
/**
* @desc submit preExam edits
* @param {event} event - click
* @this event target element - editPreExam form
*/
function editPreExam(event){
  event.preventDefault();
  var mcID = myPage.mcID.text();
  var data = jsonify($(this).serializeArray());
  data.mcID = mcID;

  sendRequest("nurseEditPreExam", "POST", data, ()=>{});
}

/**
* @desc upload a lab report
* @param {event} event - submit
* @this event target element - upload button
*/
function uploadLabReport(event){
  event.preventDefault();
  var mcID = myPage.mcID.text();
  var form = $(event.target);
  var data = new FormData(form[0]);
  data.append("mcID", mcID);

  var refresh = (res) => {
    if (!res.ret) {
      sendRequest("nurseGetLabReports", "POST", {"mcID": mcID},
      (res) => {
        if (!res.ret) {
          myPage.setLabReportAndReqs(res.labReports);
        } else {
          alert(res.ret);
        }
      });
    } else {
      alert(res.ret);
    }
  };
  sendFileRequest("nurseUploadLabReport", "POST", data, refresh);
}

// send upload lab report request
function sendFileRequest(route, type, data, successHandler){
  $.ajax({
    url: "http://localhost:5000/" + route,
    type: type,
    data: data,
    success: (res) => {
      successHandler(res);
    },
    error: (err) => {
      alert("request error");
      console.log(err);
    },
    cache: false,
    processData: false,
    contentType: false
  })
}
