/**
* @author Jingyi Zhu
* @page nurseAllAppt.js
* @import table.js, util.js
*/

/**
* @global instance of MyTable and MyModal
*/
var myTable;
var myModal;

//-------------------------document loaded---------------------------
$(document).ready(function() {
  // initialize instance
  myModal = new AppFullModal();
  myTable = new NurseTable();
  // initialize table
  var initTable = (res) => {
    myTable.initTable(res);
  };
  sendRequest("nurseOnGoingAppt", "GET", null, initTable);
  setStartOrEndDate();
});

// ---------------------capture user action--------------------------
// click table button
$('#main-table tbody').on( 'click', 'button', buttonAction);

// view ongoing applications
$("#onGoingAppt").on('click', () => goUpdateTable("nurseOnGoingAppt"));

// view future appointments
$("#futureAppt").on('click', function(){
  var dateRange = jsonifyDateRange(new Date(), new Date(), 7);
  goUpdateTable("nurseFutureAppt", dateRange);
});

// view past appointments
$("#pastAppt").on('click', function(){
  var dateRange = jsonifyDateRange(new Date(), new Date(), -7);
  goUpdateTable("nursePastAppt", dateRange);
});

// view applications rejected by the loggedin nurse
$("#rejectedApp").on('click', function(){
  var dateRange = jsonifyDateRange(new Date(), new Date(), -7);
  goUpdateTable("nurseRejectedApp", dateRange);
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
  if ($(".nav-table.active").text() == "Rejected applications") {
    myModal.setApp(data);
    var reqData = {"appID": data['appID']};
    var setComments = (res) => {myModal.setComments(res.comments)};
    sendRequest("getComments", "POST", reqData, setComments);
    myModal.show();
  } else {
    var appID = data['appID'];
    goToPage("nurseGoViewAppt/" + appID, 0);
  }
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
  var route = getRoute("nurse");
  goUpdateTable(route, dateRange);
}
