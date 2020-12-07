
var myHealthInfo;

$(document).ready(function(){
	$('#apply').button();
	// drawPagination();
	myHealthInfo = new DynamicHealthInfo();
	sendRequest("patientUpdateHealthInfo", "GET", null, (res) => myHealthInfo.update(res));
})

function goBackHome(){
	window.location.replace('http://localhost:5000/loadHomePage');
}

function drawPagination(){
	// var data = $.ajax({
	// 	url:'http://localhost:5000/getPatientRecord',
	// 	data:''
	// })


	$('.pagination-container').pagination({
		pageSize:5,
		dataSource:'http://localhost:5000/getPatientRecord',
		locator:'apps',
		totalNumberLocator:function(response){
			return response.total_number;
		},
		showPrevious:true,
		showNext:true,
		ajax:{data:{type:'appointment'}},
		alias:{
			'pageNumber':'currPage'
		},
		callback: function(data, pagination) {
        // template method of yourself
        	console.log(data);
        	$('.card-list-container').empty();
	        for(var i =0; i<data.length;i++){
		        var html = renderCard(data[i]);
		        $('.card-list-container').append(html);
	        }
    }
	})
}

function renderCard(data){
	var temp = '';
	temp += '<div class="my-container card">';
	temp += '<div class="my-container card-row card-title">';
	temp += '<div class="my-container text-wrapper"><h5>';
	temp += data['hospital'];
	temp += '</p></div></div><div class="my-container card-row"><div class="my-container text-wrapper"><p>';
	temp += data['department'];
	temp += '</p></div></div><div class="my-container card-row"><div class="my-container text-wrapper"><p>';
	temp += data['doctor'];
	temp += '</p></div></div><div class="my-container card-row"><div class="my-container text-wrapper"><p>time</p></div></div>';
	temp += '<div class="my-container status pending"><div class="my-container"><p>';
	temp += data['status'];
	temp += '</p></div></div></div>';

	return temp;



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
			myHealthInfo.updateHidden();
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
