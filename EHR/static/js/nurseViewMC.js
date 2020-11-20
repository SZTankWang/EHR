/**
* @author Jingyi Zhu
* @html nurseViewMC.html
*/

/**
* @global instance of MyTable and MyModal
*/
var myTable;
var myModal;

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
  sendRequest("ViewMC", "GET", null, initTable);
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
  myModal.setApp(data);
  myModal.setMCID(data['mcID']);
  var reqData = {"appID": data['appID']};
  var setComments = (res) => {myModal.setComments(res.comments)};
  sendRequest("GetComments", "POST", reqData, setComments);
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
