/**
* @author Jingyi Zhu
* @page nurseViewAppt.html
* @import util.js, apptAndMC.js
*/

/**
* @global instance of MCPage
*/
var mcPage;

//-------------------------document loaded---------------------------
$(document).ready(function() {
    $("select").empty();
    // initialize instance
    mcPage = new MCPage();
    // request and fill in comments
    const appID = mcPage.appID.text();
    const appData = {"appID": appID};
    var setComments = (res) => {
      mcPage.setComments(res.comments);
    };
    sendRequest("nurseGetComments", "POST", appData, setComments);
    // request and fill in medical record data
    const mcID = mcPage.mcID.text();
    const mcData = {"mcID": mcID};
    var fillMCData = (res) => {
      if (res.ret == "0") {
        console.log(res.preExam, res.preExam.bodyTemperature);
        mcPage.setBodyTemperature(res.preExam["bodyTemperature"]);
        mcPage.setHeartRate(res.preExam["heartRate"]);
        mcPage.setHighBloodPressure(res.preExam["highBloodPressure"]);
        mcPage.setLowBloodPressure(res.preExam["lowBloodPressure"]);
        mcPage.setWeight(res.preExam["weight"]);
        mcPage.setHeight(res.preExam["height"]);
        mcPage.setState(res.preExam["state"]);
        mcPage.setDiagnosis(res.diagnosis);
        mcPage.setPrescriptions(res.prescripitions);
        mcPage.setLabReportTypes(res.labReportTypes);
        mcPage.setLabReports(res.labReports);
      } else {
        console.log("hiiiii");
        console.log(res);
        alert(res.ret);
      }
    };
    sendRequest("nurseViewAppt", "POST", mcData, fillMCData);
});


// ---------------------capture user action--------------------------
// edit preExam data
$("#editPreExam").on("submit", editPreExam);
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
  var mcID = mcPage.mcID.text();
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
  var mcID = mcPage.mcID.text();
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
    goToPage("nurseViewAppt/" + mcPage.appID.text(), 0)
  }
}

// "form#labReportForm"
// $.ajax({
//   url: "http://localhost:5000/nurseUploadLabReport",
//   type: 'POST',
//   data: data,
//   success: function(res){
//     console.log(res);
//     if (res.ret == "0") {
//       window.location.replace("http://localhost:5000/nurseViewAppt/" + $("#appID").text());
//     }
//   },
//   error: function(err) {
//     console.log(err);
//   },
//   cache: false,
//   processData: false,
//   contentType: false
// })
