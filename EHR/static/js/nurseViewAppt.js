$(document).ready(function() {
    // $("select").empty();
    // init form
    var appID = $("#appID").text();
    $.ajax({
      url: "http://localhost:5000/nurseViewAppt",
      type: 'POST',
      data: {"appID": appID},
      success: function(res){
        // $("#bodyTemperature").text(res.preExam.bodyTemperature);
        // $("#pulseRate").text(res.preExam.pulseRate);
        // $("#bloodPressure").text(res.preExam.bloodPressure);
        // $("#diagnosis").text(res.diagnosis);
        // for (let i=0; i < res.prescripitions.length; i++) {
        //   $("#prescriptions").append(newPrescriptionCard(i, prescripitions[i].id + ": " + prescripitions[i].medicine, prescripitions[i].dose, prescripitions[i].comments))
        // }
        // for (let i=0; i < res.labReportTypes.length; i++) {
        //   $(this).append(new Option(res.labReportTypes[i].typeName, res.labReportTypes[i].typeID))
        // }
        // for (let i=0; i < res.labReports.length; i++){
        //   $("#labReports").append(newLabReportCard(i, labReports[i].id + ": " + labReports[i].lr_type, labReports[i].id, labReports[i].comments))
        // }
      },
      error: function(err) {
        console.log(err);
      }
    });

    //--------------------forms--------------------
    $("#editPreExam").on("click", function(event){
      event.preventDefault();
      var appID = $("#appID").text();
      var data = jsonify($(this).parent().serializeArray());
      data.appID = appID;

      $.ajax({
        url: "http://localhost:5000/nurseEditPreExam",
        type: 'POST',
        data: data,
        success: function(res){
          console.log(res);
        }
      })
    });

    $("form#labReportForm").on("submit", function(event){
      event.preventDefault();
      var appID = $("#appID").text();
      var data = new FormData($("#labReportForm")[0]);
      data.append("appID", appID);

      $.ajax({
        url: "http://localhost:5000/nurseUploadLabReport",
        type: 'POST',
        data: data,
        success: function(res){
          console.log(res);
        },
        cache: false,
        processData: false,
        contentType: false
      })
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
