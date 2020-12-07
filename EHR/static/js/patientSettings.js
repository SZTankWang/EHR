/**
* @author Jingyi Zhu
* @page patientSettings.html
* @import util.js, settingsForm.js
*/

/**
* @global instance of Settings and HealthInfo
*/
var myForm;

//-------------------------document loaded---------------------------
$(document).ready(function() {
  // initialize instance
  myForm = new Settings();
});


// ---------------------capture user action--------------------------
// update general info
$("#info").on("submit", submitInfo);


// --------------------------event handlers----------------------------
/**
* @desc submit info form
* @param {event} submit
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
