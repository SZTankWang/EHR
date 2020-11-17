$(document).ready(function() {
    // init table
    var myTable;
    $.ajax({
      url: "http://localhost:5000/nursePendingApp",
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
              "defaultContent": '<button type="button" class="modal-button btn btn-outline-primary" data-toggle="modal" data-target="#application">View</button>'
          }]
        });
        $("#overlay").addClass("d-none");
      },
      error: function(err) {
        console.log(err);
      }
    });

    // $("#application").modal();
    // $('#application').on('shown.bs.modal', function() {
    //    $('#myInput').focus();
    // });

    // -----------table click-----------
    $('#main-table tbody').on( 'click', 'button', function () {
      var data = myTable.row( $(this).parents('tr') ).data();
      if ($(".nav-table.active").text() == "Pending applications") {
        $("#appID").text(data['appID']);
        $("#date").text(data['date']);
        $("#time").text(data['time']);
        $("#doctor").text(data['doctor']);
        $("#patient").text(data['patient']);
        $("#symptoms").text(data['symptoms']);
      } else {
        var appID = data['appID'];
        window.location.replace("http://localhost:5000/nurseGoViewAppt/" + appID);
      }
    } );

    // ----------switch table content-------------
    $("#pendingApp").on('click', function(){
      $("#overlay").removeClass("d-none");
      updateTable('PendingApp');
    });

    $("#todayAppt").on('click', function(){
      $("#overlay").removeClass("d-none");
      updateTable('TodayAppt');
    });

    function updateTable(route, data=null){
      var url = "http://localhost:5000/nurse" + route;
      var type = data ? 'POST' : 'GET';
      var btnTarget = (route == "PendingApp") ? '#application' : '#appointment';

      $.ajax({
        url: url,
        type: type,
        success: function(res){
          myTable.clear().draw();
          myTable.rows.add(res);
          myTable.columns.adjust().draw();
          $(".modal-button").each(function(){
            $(this).attr('data-target',btnTarget);
          });
          $("#overlay").addClass("d-none");
        },
        error: function(err) {
          console.log(err);
        }
      });
    }

    //--------------------forms--------------------
    $(".processAppSubmit").on("click", function(event){
      event.preventDefault();
      var appID = $("#appID1").text();
      var action = $(this).val();
      var data = $(this).parent().serializeArray();
      data = jsonify(data);
      if (action == "Reject" && !data.comments) {
        alert("Please write comments before rejecting the application.");
      } else {
        data.appID = appID;
        data.action = action;
        $.ajax({
          url: "http://localhost:5000/nurseProcessApp",
          type: 'POST',
          data: data,
          success: function(res){
            setTimeout("window.location.replace('http://localhost:5000/nurseHome')", 1000);
          },
          error: function(err) {
            console.log(err);
          }
        })
      }
    });


    //-----------------style------------------
    // main navigation
    $(".nav-main").on("click", function(event) {
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

function newPrescriptionCard(index, idAndMedicine, dose, comments){
  var card = "<div class='card card-body'> <h5 class='mb-0'> <button class='btn btn-link' data-toggle='collapse' data-target='#pre" + index + "' aria-expanded='true' aria-controls='pre" + index + "'>" + idAndMedicine + "</button> </h5> <div id='pre" + index + "' class='collapse' aria-labelledby='pre" + index + "' data-parent='#prescriptions'> <div class='card-body'>" + dose + "</div> <div class='card-body'>" + comments + "</div> </div> </div>";
  return card
}

function newLabReportCard(index, idAndType, id, comments){
  var card = "<div class='card card-body'> <h5 class='mb-0'> <button class='btn btn-link' data-toggle='collapse' data-target='#lab" + index + "' aria-expanded='true' aria-controls='lab" + index + "'>" + idAndType + "</button> </h5> <div id='lab" + index + "' class='collapse' aria-labelledby='lab" + index + "' data-parent='#labReports'> <div class='card-body'>" + id + "</div> <div class='card-body'>" + comments + "</div> </div> </div>";
  return card
}
