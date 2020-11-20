/**
* @author Jingyi Zhu
* @html nurseHome.html
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
  var initTable = (res) => myTable.initTable(res, "application");
  sendRequest("PendingApp", "GET", null, initTable);
});

// ---------------------capture user action--------------------------
// click table button
$('#main-table tbody').on( 'click', 'button', buttonAction);

// submit process application
$(".processAppSubmit").on("click", goProcessApplication);

// ----------switch table content-------------
// view pending applications
$("#pendingApp").on("click", () => goUpdateTable("PendingApp"));

// view today's appointments
$("#todayAppt").on("click", () => goUpdateTable("TodayAppt"));


// --------------------------event handlers----------------------------
/**
* @desc display modal or go to view appointment page
* @param {event} event - click
* @this event target element - view button
*/
function buttonAction(event) {
  var data = myTable.table.row( $(this).parents('tr') ).data();
  if ($(".nav-table.active").text() == "Pending applications") {
    myModal.update(data);
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
    sendRequest("ProcessApp", "POST", data, goHome);
  }
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
  var updateTable = (res) => myTable.updateTable(res, btnTarget);
  sendRequest(route, type, data, updateTable);
}


//------------------------------utilities-------------------------------

function newPrescriptionCard(index, idAndMedicine, dose, comments){
  var card = "<div class='card card-body'> <h5 class='mb-0'> <button class='btn btn-link' data-toggle='collapse' data-target='#pre" + index + "' aria-expanded='true' aria-controls='pre" + index + "'>" + idAndMedicine + "</button> </h5> <div id='pre" + index + "' class='collapse' aria-labelledby='pre" + index + "' data-parent='#prescriptions'> <div class='card-body'>" + dose + "</div> <div class='card-body'>" + comments + "</div> </div> </div>";
  return card
}

function newLabReportCard(index, idAndType, id, comments){
  var card = "<div class='card card-body'> <h5 class='mb-0'> <button class='btn btn-link' data-toggle='collapse' data-target='#lab" + index + "' aria-expanded='true' aria-controls='lab" + index + "'>" + idAndType + "</button> </h5> <div id='lab" + index + "' class='collapse' aria-labelledby='lab" + index + "' data-parent='#labReports'> <div class='card-body'>" + id + "</div> <div class='card-body'>" + comments + "</div> </div> </div>";
  return card
}
