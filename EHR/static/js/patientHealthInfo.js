
var myHealthInfo;

$(document).ready(function(){
	$('#apply').button();
	myHealthInfo = new DynamicHealthInfo();
	sendRequest("patientUpdateHealthInfo", "GET", null, (res) => myHealthInfo.update(res));
})

function goBackHome(){
	window.location.replace('http://localhost:5000/loadHomePage');
}

// update health info
$("#healthInfo").on("submit", submitHealthInfo);

/**
* @desc submit health form
* @param {event} submit
*/
function submitHealthInfo(event){
  event.preventDefault();
  var data = jsonify($(this).serializeArray());

  var callBack = (res) => {
    if (!res.ret) {
			toggleForm();
    } else {
			alert("Failed to submit");
		}
  };
  sendRequest("patientUpdateHealthInfo", "POST", data, callBack);
}

function toggleForm(){
	myHealthInfo.toggle();
}
