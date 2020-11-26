/**
* @author Jingyi Zhu
* @page admin.html
* @import util.js
*/


// ---------------------capture user action--------------------------
// add a new hospital
$("#addHospital").on("submit", addHospital);
// add a new department
$("#addDepartment").on("submit", addDepartment);
// add a new lab report type
$("#addLabReportType").on("submit", addLabReportType);
// update doctor/nurse affiliation
$("#updateAffiliation").on("submit", updateAffiliation);


// --------------------------event handlers----------------------------
/**
* @desc submit form
* @param {string} route
*/
function addHospital(event){
  event.preventDefault();
  var data = jsonify($(this).serializeArray());

  var callBack = (res) => {
    if (res.ret != "0") {
      alert(res.ret);
    }
  };
  sendRequest("addHospital", "POST", data, callBack);
}

/**
* @desc submit form
* @param {string} route
*/
function addDepartment(event){
  event.preventDefault();
  var data = jsonify($(this).serializeArray());

  var callBack = (res) => {
    if (res.ret != "0") {
      alert(res.ret);
    }
  };
  sendRequest("addDepartment", "POST", data, callBack);
}

/**
* @desc submit form
* @param {string} route
*/
function addLabReportType(event){
  event.preventDefault();
  var data = jsonify($(this).serializeArray());

  var callBack = (res) => {
    if (res.ret != "0") {
      alert(res.ret);
    }
  };
  sendRequest("addLabReportType", "POST", data, callBack);
}

/**
* @desc submit form
* @param {string} route
*/
function updateAffiliation(event){
  event.preventDefault();
  var data = jsonify($(this).serializeArray());

  var callBack = (res) => {
    if (res.ret != "0") {
      alert(res.ret);
    }
  };
  sendRequest("updateAffiliation", "POST", data, callBack);
}
