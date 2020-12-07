/**
* @author Jingyi Zhu
* @page doctorAllAppt.js
* @import table.js, util.js
*/

/**
* @global instance of MyTable and MyModal
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
  var dateRange = jsonifyDateRange(new Date(), new Date(), 7)
  sendRequest("doctorFutureAppt", "POST", dateRange, initTable);
  setStartOrEndDate(dateRange.startDate, dateRange.endDate);
});

// ---------------------capture user action--------------------------
// click table button
$('#main-table tbody').on( 'click', 'button', buttonAction);

// view future appointments
$("#futureAppt").on('click', function(){
  var dateRange = jsonifyDateRange(new Date(), new Date(), 7);
  goUpdateTable("doctorFutureAppt", dateRange);
});

// view past appointments
$("#pastAppt").on('click', function(){
  var dateRange = jsonifyDateRange(new Date(), new Date(), -7);
  goUpdateTable("doctorPastAppt", dateRange);
});

//change date range
$("#dateRange").on('submit', updateDateRange);


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
* @param {array} data - default null or jsonified date range
*/
function goUpdateTable(route, dateRange=null){
  var type = dateRange ? 'POST' : 'GET';
  var updateTable = (res) => {
    myTable.updateTable(res);
  };
  sendRequest(route, type, dateRange, updateTable);
  setStartOrEndDate(dateRange ? dateRange.startDate : null, dateRange ? dateRange.endDate : null);
}

/**
* @desc update date range and stay in the current tab
* @param {event} event - submit
*/
function updateDateRange(event){
  event.preventDefault();
  var dateRange = $(this).serializeArray();
  dateRange = jsonify(dateRange);
  var route = getRoute("doctor");
  goUpdateTable(route, dateRange);
}
