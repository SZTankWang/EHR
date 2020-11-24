/**
* @author Jingyi Zhu
* @page admin.html
* @import util.js
*/


// ---------------------capture user action--------------------------
// update general info
$("#info").on("submit", (event) => {event.preventDefault(); submitForm("patientUpdateInfo");});
// update health info
$("#healthInfo").on("submit", (event) => {event.preventDefault(); submitForm("patientUpdateHealthInfo");});

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
