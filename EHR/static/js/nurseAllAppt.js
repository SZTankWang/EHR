/**
* @author Jingyi Zhu
* @html nurseAllAppt.js
*/

/**
* @global instance of MyTable and MyModal
*/
var myTable;
var myModal;

//-------------------------document loaded---------------------------
$(document).ready(function() {
  // initialize instance
  myModal = new HomeModal();
  myTable = new HomeTable();
  // initialize table
  var initTable = (res) => myTable.initTable(res, "appointment");
  sendRequest("FutureAppt", "GET", null, initTable);
});

// ---------------------capture user action--------------------------
// click table button
$('#main-table tbody').on( 'click', 'button', buttonAction);

// ----------switch table content-------------
// view ongoing applications
$("#onGoingAppt").on('click', () => goUpdateTable("OnGoingAppt"));

// view future appointments
$("#futureAppt").on('click', () => goUpdateTable("FutureAppt"));

// view past appointments
$("#pastAppt").on('click', function(){
  var dateRange = jsonifyDateRange(new Date(), new Date(), 7);
  goUpdateTable("PastAppt", dateRange);
});

// view applications rejected by the loggedin nurse
$("#rejectedApp").on('click', function(){
  var dateRange = jsonifyDateRange(new Date(), new Date(), 7);
  goUpdateTable("RejectedApp", dateRange);
});


// --------------------------event handlers----------------------------
/**
* @desc display modal or go to view appointment page
* @param {event} event - click
* @this event target element - view button
*/
function buttonAction(event) {
  var data = myTable.row( $(this).parents('tr') ).data();
  if ($(".nav-table.active").text() == "Rejected applications") {
    myModal.update(data);
    var reqData = {"appID": data['appID']};
    var setComments = (res) => {$("#comments").text(res.comments)};
    sendRequest("GetComments", "POST", reqData, setComments);
  } else {
    event.preventDefault();
    var appID = data['appID'];
    goToPage("nurseGoViewAppt/" + appID, 0);
  }
}

/**
* @desc request data and update table
* @param {string} route
* @param {array} data - default null or jsonified date range
*/
function goUpdateTable(route, data=null){
  var type = data ? 'POST' : 'GET';
  var btnTarget = (route == "RejectedApp") ? '#application' : '#appointment';
  $("#overlay").removeClass("d-none");
  var updateTable = (res) => myTable.updateTable(res, btnTarget);
  sendRequest(route, type, data, updateTable);
}

//------------------------------utilities-------------------------------

function jsonifyDateRange(startDate, endDate, range=null){
  if (range) {
    endDate.setDate(startDate.getDate() + 7);
  }
  var startDateStr = startDate.toISOString().split('T')[0];
  var endDateStr = endDate.toISOString().split('T')[0];
  var data = {"startDate": startDateStr, "endDate": endDateStr};
  return data;
}
