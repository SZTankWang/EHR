/**
* @author Jingyi Zhu
* @page doctorNurseSettings.html
* @import settingsForm.js
*/

/**
* @global instance of Settings
*/
var myForm;

//-------------------------document loaded---------------------------
$(document).ready(function() {
  // initialize instance
  myForm = new Settings();
});

// ---------------------capture user action--------------------------
// click table button
$('#info').on( 'submit', updateSettings);

// --------------------------event handlers----------------------------
/**
* @desc update info
* @param {event} event - submit
* @this form
*/
function updateSettings(event){
  event.preventDefault();
  var data = jsonify($(this).serializeArray())

  var updateForm = (res) => {
    if (res.ret == "0"){
      myForm.update(res);
    } else {
      alert("Failed to submit");
    }
  };
  sendRequest("doctorNurseUpdateInfo", "POST", data, updateForm);
}
