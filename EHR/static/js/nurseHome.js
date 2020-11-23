/**
* @author Jingyi Zhu
* @page nurseHome.html
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
  myModal = new AppModal();
  myTable = new HomeTable();
  // initialize table
  var initTable = (res) => {
    myTable.initTable(res, "application");
    // $("#overlay").addClass("d-none");
  };
  sendRequest("nursePendingApp", "GET", null, initTable);
});

// ---------------------capture user action--------------------------
// click table button
$('#main-table tbody').on( 'click', 'button', buttonAction);

// submit process application
$(".processAppSubmit").on("click", goProcessApplication);

// ----------switch table content-------------
// view pending applications
$("#pendingApp").on("click", () => goUpdateTable("nursePendingApp"));

// view today's appointments
$("#todayAppt").on("click", () => goUpdateTable("nurseTodayAppt"));


// --------------------------event handlers----------------------------
/**
* @desc display modal or go to view appointment page
* @param {event} event - click
* @this event target element - view button
*/
function buttonAction(event) {
  var data = myTable.table.row( $(this).parents('tr') ).data();
  if ($(".nav-table.active").text() == "Pending applications") {
    myModal.setApp(data);
  } else {
    event.preventDefault();
    var appID = data['appID'];
    goToPage("nurseGoViewAppt/" + appID, 0);
  }
}

/**
* @desc process application
* @param {event} event - click
* @this event target element - submit button
*/
function goProcessApplication(event){
  event.preventDefault();
  var action = $(this).val();
  var data = $(this).parent().serializeArray();
  data = jsonify(data);

  // if reject: comments shouldn't be null
  if (action == "Reject" && !data.comments) {
    alert("Please write comments before rejecting the application.");
  } else {
    var appID = $("#appID").text()
    data.appID = appID;
    data.action = action;
    var goHome = () => goToPage("nurseHome", 1000);
    sendRequest("nurseProcessApp", "POST", data, goHome);
  }
}

/**
* @desc request data and update table
* @param {string} route
* @param {array} data - default null
*/
function goUpdateTable(route, data=null){
  var type = data ? 'POST' : 'GET';
  var btnTarget = (route == "nursePendingApp") ? '#application' : '#appointment';
  // $("#overlay").removeClass("d-none");
  var updateTable = (res) => {
    myTable.updateTable(res, btnTarget);
    // $("#overlay").addClass("d-none");
  };
  sendRequest(route, type, data, updateTable);
}
