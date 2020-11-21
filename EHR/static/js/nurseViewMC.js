/**
* @author Jingyi Zhu
* @page nurseViewMC.html
* @import util.js, apptAndMC.js
*/

/**
* @global instance of MCModal
*/
var mcModal;
var mcTable;

//-------------------------document loaded---------------------------
$(document).ready(function() {
  // initialize instance
  myModal = new MCModal();
  myTable = new MCTable();
  // initialize table
  var initTable = (res) => {
    myTable.initTable(res);
    $("#overlay").addClass("d-none");
  };
  sendRequest("nurseViewMC", "GET", null, initTable);
});

// ---------------------capture user action--------------------------
// click table button
$('#main-table tbody').on( 'click', 'button', buttonAction);

// --------------------------event handlers----------------------------
/**
* @desc display modal
* @param {event} event - click
*/
function buttonAction(event) {
  var data = myTable.table.row( $(this).parents('tr') ).data();
  data['patient'] = $("#patientName").text();
  const mcID = data['mcID'];
  myModal.setMCID(mcID);
  myModal.setApp(data);
  // request and fill in comments
  var appData = {"appID": data['appID']};
  var fillAppData = (res) => {
    myModal.setAppStatus(res.appStatus);
    myModal.setComments(res.comments);
  };
  sendRequest("nurseGetComments", "POST", appData, fillAppData);
  // request and fill in medical record data
  const mcData = {"mcID": mcID};
  var fillMCData = (res) => {
    mcModal.setBodyTemperature(res.preExam.bodyTemperature);
    mcModal.setHeartRate(res.preExam.heartRate);
    mcModal.setHighBloodPressure(res.preExam.highBloodPressure);
    mcModal.setLowBloodPressure(res.preExam.lowBloodPressure);
    mcModal.setWeight(res.preExam.weight);
    mcModal.setHeight(res.preExam.height);
    mcModal.setState(res.preExam.state);
    mcModal.setDiagnosis(res.diagnosis);
    mcModal.setPrescriptions(res.prescripitions);
    mcModal.setLabReportTypes(res.labReportTypes);
    mcModal.setLabReports(res.labReports);
  };
  sendRequest("nurseViewAppt", "POST", mcData, fillMCData);
}

/**
* @desc request data and update table
* @param {string} route
* @param {array} data - default null
*/
function goUpdateTable(route, data=null){
  var type = data ? 'POST' : 'GET';
  var btnTarget = (route == "PendingApp") ? '#application' : '#appointment';
  $("#overlay").removeClass("d-none");
  var updateTable = (res) => {
    myTable.updateTable(res, btnTarget);
    $("#overlay").addClass("d-none");
  };
  sendRequest(route, type, data, updateTable);
}
