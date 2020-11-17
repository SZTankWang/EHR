$(document).ready(function() {
    // init table
    var myTable;
    $.ajax({
      url: "http://localhost:5000/nurseOnGoingApp",
      type: 'GET',
      success: function(res){
        myTable = $("#main-table").DataTable({
          "data": res,
          "columns" : [
              { "data" : "appID", "title": "Application ID" },
              { "data" : "date", "title": "Date" },
              { "data" : "time", "title": "Time" },
              { "data" : "doctor", "title": "Doctor" },
              { "data" : "patient", "title": "Patient" },
              { "data" : "symptoms", "title": "Symptoms" },
              { "data" : "", "title": "" }
              // , "render": (data, type, row, meta) => `<button type="button" class="modal-button btn btn-outline-primary" data-toggle="modal" data-target="#application">View</button>`
          ],
          "columnDefs": [{
              "targets": -1,
              "orderable": false,
              "searchable": false,
              "data": null,
              "defaultContent": '<button type="button" class="modal-button btn btn-outline-primary" data-toggle="modal" data-target="#appointment">View</button>'
          }]
        });
      }
    });

    // $("#application").modal();
    // $('#application').on('shown.bs.modal', function() {
    //    $('#myInput').focus();
    // });

    // -----------show modal-----------
    $('#main-table tbody').on( 'click', 'button', function () {
      var data = myTable.row( $(this).parents('tr') ).data();
      if ($(".nav-table.active").text() == "Ongoing appointments") {
        var code = "1";
      } else {
        var code = "2";
      }
      $("#appID"+code).text(data['appID']);
      $("#date"+code).text(data['date']);
      $("#time"+code).text(data['time']);
      $("#doctor"+code).text(data['doctor']);
      $("#patient"+code).text(data['patient']);
      $("#symptoms"+code).text(data['symptoms']);
      // if (code == "2"){
      // 	$.ajax({
      // 		url: "http://localhost:5000/viewAppt",
      // 		type: 'POST',
      // 		data: {"appID": data['appID']},
      // 		success: function(res){
      // 			$("bodyTemperature").text(res.preExam.bodyTemperature);
      // 			$("pulseRate").text(res.preExam.pulseRate);
      // 			$("bloodPressure").text(res.preExam.bloodPressure);
      // 			$("diagnosis").text(res.diagnosis);
      // 			for (let i=0; i < res.prescripitions.length; i++) {
      // 				$("prescriptions").append()
      // 			}
      // 			for (let i=0; i < res.labReports.length; i++){
      //
      // 			}
      // 		}
      // 	});
      // }
    } );

    // ----------switch table content-------------
    $("#onGoingApp").on('click', function(){
      updateTable('OnGoingApp');
    });

    $("#futureAppt").on('click', function(){
      updateTable('FutureAppt');
    });

    $("#pastAppt").on('click', function(){
      var dateRange = jsonifyDateRange(new Date(), new Date(), 7);
      updateTable('PastAppt', dateRange);
    });

    $("#rejectedApp").on('click', function(){
      var dateRange = jsonifyDateRange(new Date(), new Date(), 7);
      updateTable('RejectedApp', dateRange);
    });

    function updateTable(route, data=null){
      var url = "http://localhost:5000/nurse" + route;
      var type = data ? 'POST' : 'GET';
      var btnTarget = (route == "RejectedApp") ? '#application' : '#appointment';

      $.ajax({
        url: url,
        type: type,
        data: data,
        success: function(res){
          myTable.clear().draw();
          myTable.rows.add(res);
          myTable.columns.adjust().draw();
          $(".modal-button").each(function(){
            $(this).attr('data-target',btnTarget);
          });
        }
      });
    }

    //--------------------form--------------------
    $(":submit").on("click", function(event){
      event.preventDefault();
      var appID = $("#appID1").text();
      var action = $(this).val();
      var data = $(this).parent().serializeArray();
      data = jsonify(data);
      if (action == "Reject" && !data.comments) {
        alert("Comments is required to reject the application.");
      } else {
        data.appID = appID;
        data.action = action;
        $.ajax({
          url: "http://localhost:5000/nurseProcessApp",
          type: 'POST',
          data: data,
          success: function(res){
            setTimeout("window.location.replace('http://localhost:5000/nurseHome')", 1000);
          }
        })
      }
    });

    //-----------------go to createAppt page------------------
    $("#goCreateAppt").on("click", function(event) {
      setTimeout("window.location.replace('http://localhost:5000/nurseGoCreateAppt')", 1000);
    });

    //-----------------style------------------
    // main navigation
    $(".nav-main").on("click", function(event) {
        event.preventDefault();
        var clickedItem = $(this);
        $(".nav-main").each( function() {
          if ($(this).hasClass("active disabled")) {
            $(this).removeClass("active disabled");
          }
        });
        clickedItem.addClass("active disabled");
    });

    // table navigation
    $(".nav-table").on("click", function(event) {
        event.preventDefault();
        var clickedItem = $(this);
        $(".nav-table").each( function() {
            if ($(this).hasClass("active disabled")) {
              $(this).removeClass("active disabled");
            }
        });
        clickedItem.addClass("active disabled");
    });
});

//------------utilities-------------
function jsonify(data){
  var obj = {};
  for(var i=0;i<data.length;i++){
    obj[data[i].name]=data[i].value;
  }
  return obj;
}

function jsonifyDateRange(startDate, endDate, range=null){
  if (range) {
    endDate.setDate(startDate.getDate() + 7);
  }
  var startDateStr = startDate.toISOString().split('T')[0];
  var endDateStr = endDate.toISOString().split('T')[0];
  var data = {"startDate": startDateStr, "endDate": endDateStr};
  return data;
}
