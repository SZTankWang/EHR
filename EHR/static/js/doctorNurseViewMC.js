/**
* @author Jingyi Zhu
* @page doctorNurseViewMC.html
* @import table.js, modal.js, util.js, apptAndMC.js
*/

/**
* @global instance of MCModal
*/
var myModal;
var myTable;

//-------------------------document loaded---------------------------
$(document).ready(function() {
  // initialize instance
  myModal = new MCModal();
  myTable = new MCTable();
  // initialize table
  var initTable = (res) => {
    myTable.initTable(res.appts);
    // $("#overlay").addClass("d-none");
  };
  var patientID = $("#patientID").text();
  var data = {"patientID": patientID};
  sendRequest("doctorNurseViewMC", "POST", data, initTable);
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
  // request and fill in app status and comments
  myModal.loadAppInfo(data['appID']);
  // request and fill in medical record data
  myModal.loadMCInfo(mcID);
}

/**
* @desc request data and update table
* @param {string} route
* @param {array} data - default null
*/
function goUpdateTable(route, data=null){
  var type = data ? 'POST' : 'GET';
  // $("#overlay").removeClass("d-none");
  var updateTable = (res) => {
    myTable.updateTable(res);
    // $("#overlay").addClass("d-none");
  };
  sendRequest(route, type, data, updateTable);
}
