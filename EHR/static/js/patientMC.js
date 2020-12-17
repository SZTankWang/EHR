/**
* @global instance of MCModal
*/
var myModal;

$(document).ready(function(){
	$('#apply').button();
	drawPagination();
	myModal = new MCModal();
})

function drawPagination(){
	// var data = $.ajax({
	// 	url:'http://localhost:5000/getPatientRecord',
	// 	data:''
	// })


	$('.pagination-container').pagination({
		pageSize:5,
		dataSource:'http://localhost:5000/getPatientRecord',
		locator:'mcs',
		totalNumberLocator:function(response){
			return response.total_number;
		},
		showPrevious:true,
		showNext:true,
		ajax:{data:{type:'medical_record'}},
		alias:{
			'pageNumber':'currPage'
		},
		callback: function(data, pagination) {
        // template method of yourself
        	console.log(data);
        	$('.card-list-container').empty();
			$('#total_count').empty();
        	$('#total_count').html(data.length);

	        for(var i =0; i<data.length;i++){
		        var html = renderCard(data[i]);
		        $('.card-list-container').append(html);
	        }
    }
	})
}

function renderCard(data){
	var temp = '';
	temp += '<div class="my-container card" onclick="buttonAction(this)">';
	temp += '<div class="my-container card-row"><form class="d-none"><input type="text" name="getAppID" value=' + data['appID'] + '><input type="text" name="getMCID" value=' + data['mcID'] + '></form></div>';
	temp += '<div class="my-container card-row card-title">';
	temp += '<div class="my-container text-wrapper"><h5>';
	temp += data['hospital'];
	temp += '</p></div></div><div class="my-container card-row"><div class="my-container text-wrapper"><p>';
	temp += data['department'];
	temp += '</p></div></div><div class="my-container card-row"><div class="my-container text-wrapper"><p>';
	temp += "Doctor: " + data['doctor'];
	temp += '</p></div></div><div class="my-container card-row"><div class="my-container text-wrapper"><p>';
	temp += data['date'] + " " + data['time'];
	temp += '</p></div></div></div>';

	return temp;
}

// --------------------------event handlers----------------------------
/**
* @author Jingyi Zhu
* @desc display modal
* @param {element} e - card
*/
function buttonAction(e) {
  var data = jsonify($(e).find("form").serializeArray());

  myModal.setMCID(data['getMCID']);
	//get appointment data
	sendRequest("/patientGetApp", "POST", {"appID": data['getAppID']}, (res) => myModal.setApp(res));
  // request and fill in app status and comments
  myModal.loadAppInfo(data['getAppID']);
  // request and fill in medical record data
  myModal.loadMCInfo(data['getMCID'], "patientViewAppt");
  console.log(myModal.myself);
	myModal.show();
}
