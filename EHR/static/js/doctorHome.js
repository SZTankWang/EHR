/**
* @author Jingyi Zhu
* @page doctorHome.html
* @import util.js, table.js
*/

/**
* @global instance of MyTable
*/
var myTable;

//-------------------------document loaded---------------------------
$(document).ready(function() {
  // initialize instance
  myTable = new DoctorTable();
  // initialize table
  var initTable = (res) => {
    myTable.initTable(res);
  };
  sendRequest("doctorOnGoingAppt", "GET", null, initTable);
});

// ---------------------capture user action--------------------------
// click table button
$('#main-table tbody').on( 'click', 'button', buttonAction);
// view pending applications
$("#onGoingAppt").on("click", () => goUpdateTable("doctorOnGoingAppt"));
// view today's appointments
$("#todayAppt").on("click", () => goUpdateTable("doctorTodayAppt"));


// --------------------------event handlers----------------------------
/**
* @desc display modal or go to view appointment page
* @param {event} event - click
* @this event target element - view button
*/
function buttonAction(event) {
  event.preventDefault();
  var data = myTable.table.row( $(this).parents('tr') ).data();
  var appID = data['appID'];
  goToPage("doctorGoViewAppt/" + appID, 0);
}

/**
* @desc request data and update table
* @param {string} route
* @param {array} data - default null
*/
function goUpdateTable(route, data=null){
  var type = data ? 'POST' : 'GET';
  var updateTable = (res) => {
    myTable.updateTable(res);
  };
  sendRequest(route, type, data, updateTable);
}
