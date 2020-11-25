/**
* @author Jingyi Zhu
* @page doctorViewAppt.html
* @import util.js, apptAndMC.js
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
    // request and fill in medical record data
    const mcID = myPage.mcID.text();
    myPage.loadMCInfo(mcID);
});


// ---------------------capture user action--------------------------
// add prescription
$("#prescriptionForm").on("submit", editPreExam);
// upload a lab report
$("#labReportForm").on("submit", uploadLabReport);


// --------------------------event handlers----------------------------
/**
* @desc submit preExam edits
* @param {event} event - click
* @this event target element - edit button
*/
function editPreExam(event){
  event.preventDefault();
  var mcID = myPage.mcID.text();
  var data = jsonify($(this).serializeArray());
  data.mcID = mcID;

  var refresh = (res) => {refreshOnSuccess(res)};
  sendRequest("nurseEditPreExam", "POST", data, refresh);
}

/**
* @desc upload a lab report
* @param {event} event - submit
* @this event target element - upload button
*/
function uploadLabReport(event){
  event.preventDefault();
  var mcID = myPage.mcID.text();
  var data = new FormData($("#labReportForm")[0]);
  data.append("mcID", mcID);

  var refresh = (res) => {refreshOnSuccess(res)};
  sendFileRequest("UploadLabReport", "POST", data, refresh);
}

// send upload lab report request
function sendFileRequest(route, type, data, successHandler){
  $.ajax({
    url: "http://localhost:5000/nurse" + route,
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

// refresh page if submission is successful
function refreshOnSuccess(res){
  if (res.ret == "0") {
    goToPage("nurseGoViewAppt/" + myPage.appID.text(), 0)
  }
}
