/**
* @author Jingyi Zhu
* @page nurseCreateAppt.html
* @import util.js
*/

//-------------------------document loaded---------------------------
$(document).ready(function() {
    $("select").empty();
    $("#ret span").removeClass("visible");
    $("#ret span").addClass("invisible");
    // display department options for the nurse's hospital
    getAndDisplay("hospital");
});

// ---------------------capture user action--------------------------
// display doctor options for the department
$("#department").on("change", () => getAndDisplay("dept"));
// display time slot options for the doctor
$("#doctor").on("change", () => getAndDisplay("doctor"));
// create appointment
$("#createAppt").on("submit", createAppt);

// --------------------------event handlers----------------------------
/**
* @desc request a list of options and display them in <select>
* @param {string} target - hospital/dept/doctor
*/
function getAndDisplay(target){
  var route, type, data, display;
  var option = new Option("", "");
  option.disabled = true;
  option.defaultSelected = true;

  if (target == "hospital") {
    route = "nurseGetDepartmentsForNurse";
    type = "GET";
    data = null;

    display = function(res){
      $("#department").empty();
      $("#department").append(option);
      for (let i=0; i < res.length; i++) {
        $("#department").append(new Option(res[i].deptName, res[i].deptID));
      }
    };
  } else {
    type = "POST";
    idname = target + "ID";
    data = {};
    var id;

    if (target == "dept") {
      id = $("#department").children(":selected").val();
      data[idname] = id;
      route = "nurseGetDoctorsForDepartment";

      display = function(res){
        $("#doctor").empty();
        $("#doctor").append(option);
        for (let i=0; i < res.length; i++) {
          $("#doctor").append(new Option(res[i].doctorName, res[i].doctorID));
        }
        // $("#doctor").attr("disabled", false);
      };
    } else {
      id = $("#doctor").children(":selected").val();
      data[idname] = id;
      route = "nurseGetSlotsForDoctor";

      display = function(res){
        $("#slot").empty();
        $("#slot").append(option);
        for (let i=0; i < res.length; i++) {
          $("#slot").append(new Option(res[i].slotDateTime, res[i].slotID))
        }
      };
    }

  }
  sendRequest(route, type, data, display);
}

/**
* @desc request a list of options and display them in <select>
* @param {string} target - hospital/dept/doctor
*/
function createAppt(event){
  event.preventDefault();
  var data = $(this).serializeArray();
  var afterCreateAppt = function(res){
    if (res.ret == "0") {
      $("#ret span").text("Success");
    } else {
      $("#ret span").text("Error: failed to create the appointment");
    }
    $("#ret span").removeClass("invisible");
    $("#ret span").addClass("visible");
    goToPage("nurseHome", 1000);
  };
  sendRequest("nurseCreateAppt", "POST", data, afterCreateAppt);
}
