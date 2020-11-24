/**
* @author Jingyi Zhu
* @page admin.html
* @import util.js
*/


// ---------------------capture user action--------------------------
// add a new hospital
$("#addHospital").on("submit", (event) => {event.preventDefault(); submitForm("addHospital");});
// add a new department
$("#addDepartment").on("submit", (event) => {event.preventDefault(); submitForm("addDepartment");});
// add a new lab report type
$("#addLabReportType").on("submit", (event) => {event.preventDefault(); submitForm("addLabReportType");});
// update doctor/nurse affiliation
$("#updateAffiliation").on("submit", (event) => {event.preventDefault(); submitForm("updateAffiliation");});


// --------------------------event handlers----------------------------
/**
* @desc submit form
* @param {string} route
*/
function submitForm(route){
  var data = jsonify($(this).serializeArray());

  var callBack = (res) => {
    if (res.ret != "0") {
      alert(res.ret);
    }
  };
  sendRequest(route, "POST", data, callBack);
}
