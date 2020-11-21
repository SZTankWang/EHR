/**
* @author Jingyi Zhu
* @page nurseCreateAppt.html
* @import util.js
*/

//-------------------------document loaded---------------------------
$(document).ready(function() {
    $("#department").addAttr("disabled");
    $("#doctor").addAttr("disabled");
    $("#slot").addAttr("disabled");
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
  if (target == "hospital") {
    route = "nurseGetDepartmentsForNurse";
    type = "GET";
    data = null;
    display = function(res){
      for (let i=0; i < res.length; i++) {
        $("#department").append(new Option(res[i].deptName, res[i].deptID));
      }
      $("#department").removeAttr("disabled");
    };
  } else {
    type = "POST";
    var id = $(this).children(":selected").value();
    data = {target + "ID": id};
    if (target == "dept") {
      route = "nurseGetDoctorsForDepartment";
      display = function(res){
        for (let i=0; i < res.length; i++) {
          $("#doctor").append(new Option(res[i].doctorName, res[i].doctorID));
        }
        $("#doctor").removeAttr("disabled");
      };
    } else {
      route = "nurseGetSlotsForDoctor";
      display = function(res){
        for (let i=0; i < res.length; i++) {
          $("#slot").append(new Option(res[i].slotDateTime, res[i].slotID))
        }
        $("#slot").removeAttr("disabled");
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
    goToPage("nurseHome", 300);
  };
  sendRequest("nurseCreateAppt", "POST", data, afterCreateAppt);
}
