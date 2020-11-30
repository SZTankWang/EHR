/**
* @author Jingyi Zhu
* @page patientSettings.html
* @import util.js, settingsForm.js
*/

/**
* @global instance of Settings and HealthInfo
*/
var myForm;
var myHealthInfo;

//-------------------------document loaded---------------------------
$(document).ready(function() {
  // initialize instance
  myForm = new Settings();
  myHealthInfo = new HealthInfo();
  sendRequest("patientUpdateHealthInfo", "GET", null, (res) => myHealthInfo.update(res))
});


// ---------------------capture user action--------------------------
// update general info
$("#info").on("submit", submitInfo);
// update health info
$("#healthInfo").on("submit", submitHealthInfo);

// --------------------------event handlers----------------------------
/**
* @desc submit form
* @param {string} route
*/
function submitInfo(event){
  event.preventDefault();
  var data = jsonify($(this).serializeArray());

  var callBack = (res) => {
    if (res.ret != "0") {
      alert("Failed to submit");
    }
  };
  sendRequest("patientUpdateInfo", "POST", data, callBack);
}

/**
* @desc submit form
* @param {string} route
*/
function submitHealthInfo(route, data){
  event.preventDefault();
  var data = jsonify($(this).serializeArray());

  var callBack = (res) => {
    if (res.ret != "0") {
      alert("Failed to submit");
    }
  };
  sendRequest("patientUpdateHealthInfo", "POST", data, callBack);
}
