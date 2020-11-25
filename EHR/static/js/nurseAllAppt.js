/**
* @author Jingyi Zhu
* @page nurseAllAppt.js
* @import util.js
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
    // $("#overlay").addClass("d-none");
  };
  sendRequest("nurseOnGoingAppt", "GET", null, initTable);
  setStartOrEndDate();
});

// ---------------------capture user action--------------------------
// click table button
$('#main-table tbody').on( 'click', 'button', buttonAction);

// ----------switch table content-------------
// view ongoing applications
$("#onGoingAppt").on('click', () => goUpdateTable("nurseOnGoingAppt"));

// view future appointments
$("#futureAppt").on('click', () => goUpdateTable("nurseFutureAppt"));

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
    if ($(".nav-table.active").text() == "Past appointments") {
      goToPage("nurseGoViewApptPast/" + appID, 0);
    } else {
      goToPage("nurseGoViewAppt/" + appID, 0);
    }
  }
}

/**
* @desc request data and update table
* @param {string} route
* @param {array} data - default null or jsonified date range
*/
function goUpdateTable(route, dateRange=null){
  var type = dateRange ? 'POST' : 'GET';
  // $("#overlay").removeClass("d-none");
  var updateTable = (res) => {
    myTable.updateTable(res);
    // $("#overlay").addClass("d-none");
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
  var route = getRoute();
  goUpdateTable(route, dateRange);
}

//------------------------------utilities-------------------------------
function jsonifyDateRange(startDate, endDate, range=0){
  if (range < 0) {
    startDate.setDate(endDate.getDate() + range);
  } else if (range > 0) {
    endDate.setDate(startDate.getDate() + range);
  }

  var startDateStr = getFullDate(startDate);
  var endDateStr = getFullDate(endDate);
  var dateRange = {"startDate": startDateStr, "endDate": endDateStr};
  return dateRange;
}

function getRoute(){
  if ($(".nav-table.active").text() == "Ongoing appointments") {
    return "nurseOnGoingAppt";
  } else if ($(".nav-table.active").text() == "Future appointments") {
    return "nurseFutureAppt";
  } else if ($(".nav-table.active").text() == "Past appointments") {
    return "nursePastAppt";
  } else {
    return "nurseRejectedApp";
  }
}

function setStartOrEndDate(startDate=null, endDate=null){
  if (!startDate && !endDate) {
    startDate = getFullDate(new Date());
  }
  if ($(".nav-table.active").text() == "Ongoing appointments") {
    switchInputAttr (true, true, startDate, startDate, true);
  } else if ($(".nav-table.active").text() == "Future appointments") {
    switchInputAttr (true, false, startDate, endDate, false);
  } else if ($(".nav-table.active").text() == "Past appointments") {
    switchInputAttr (false, true, startDate, endDate, false);
  } else {
    switchInputAttr (false, false, startDate, endDate, false);
  }
}

function switchInputAttr (start, end, startDate, endDate, submit) {
  $("#startDate").prop("readonly", start);
  $("#endDate").prop("readonly", end);
  $("#startDate").prop("value", startDate);
  $("#endDate").prop("value", endDate);
  $("#applyRange").prop("disabled", submit);
}
