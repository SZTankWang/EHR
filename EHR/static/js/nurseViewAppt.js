/**
* @author Jingyi Zhu
* @html nurseViewAppt.html
*/

$(document).ready(function() {
    $("select").empty();
    // init form
    var mcID = $("#mcID").text();
    $.ajax({
      url: "http://localhost:5000/nurseViewAppt",
      type: 'POST',
      data: {"mcID": mcID},
      success: function(res){
        $("#bodyTemperature").text(res.preExam.bodyTemperature);
        $("#pulseRate").text(res.preExam.pulseRate);
        $("#bloodPressure").text(res.preExam.bloodPressure);
        $("#diagnosis").text(res.diagnosis);
        for (let i=0; i < res.prescripitions.length; i++) {
          $("#prescriptions").append(newPrescriptionCard(i+1, prescripitions[i].id + ": " + prescripitions[i].medicine, prescripitions[i].dose, prescripitions[i].comments));
        }
        for (let i=0; i < res.labReportTypes.length; i++) {
          $(this).append(new Option(res.labReportTypes[i].typeName, res.labReportTypes[i].typeID));
        }
        for (let i=0; i < res.labReports.length; i++){
          $("#labReports").append(newLabReportCard(i+1, labReports[i].lr_type, labReports[i].id, labReports[i].comments));
        }
      },
      error: function(err) {
        console.log(err);
      }
    });

    //--------------get the lab report-----------------
    $(".lr-btn").on("click", function(event){
      const targetCard = $(this).attr("data-target");
      const button = $(targetCard+" a");
      // if (button.attr('href') == ""){
      const lrID = button.attr('id').slice(6);
      $.ajax({
        url: "http://localhost:5000/nursePreviewLR",
        type: 'POST',
        data: {"lrID": lrID},
        success: function(res){
          if (res.labReport) {
            button.attr('href', URL.createObjectURL(res.labReport));
          }
        },
        error: function(err) {
          console.log(err);
        }
      });
      // }
    });

    $(".preview-btn").on("click", function(event){
      if ($(this).attr('href') == "") {
        alert("Lab report empty");
        event.preventDefault();
      }
    })

    //--------------------forms--------------------
    $("#editPreExam").on("click", function(event){
      event.preventDefault();
      var mcID = $("#mcID").text();
      var data = jsonify($(this).parent().serializeArray());
      data.appID = mcID;

      $.ajax({
        url: "http://localhost:5000/nurseEditPreExam",
        type: 'POST',
        data: data,
        success: function(res){
          console.log(res);
          if (res.ret == "0") {
            window.location.replace("http://localhost:5000/nurseViewAppt/" + $("#appID").text());
          }
        },
        error: function(err) {
          console.log(err);
        }
      })
    });

    $("form#labReportForm").on("submit", function(event){
      event.preventDefault();
      var mcID = $("#mcID").text();
      var data = new FormData($("#labReportForm")[0]);
      data.append("mcID", mcID);

      $.ajax({
        url: "http://localhost:5000/nurseUploadLabReport",
        type: 'POST',
        data: data,
        success: function(res){
          console.log(res);
          if (res.ret == "0") {
            window.location.replace("http://localhost:5000/nurseViewAppt/" + $("#appID").text());
          }
        },
        error: function(err) {
          console.log(err);
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

function newLabReportCard(index, type, id, comments){
  var card = "<div class='card card-body'> <h5 class='mb-0'> <button class='lr-btn btn btn-link' data-toggle='collapse' data-target='#lab" + index + "' aria-expanded='true' aria-controls='lab" + index + "'>" + index + ". " + type + "</button> </h5> <div id='lab" + index + "' class='collapse' aria-labelledby='lab" + index + "' data-parent='#labReports'> <hr> <div class='card-body'><span>Lab report id: " + id + " </span><a id='preview" + id + "' class='preview-btn btn btn-sm btn-outline-primary' href='' target='_blank'>preview</a> </div> <div class='card-body'>" + comments + "</div> </div> </div>";
  return card
}
