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


// ---------------------capture user action--------------------------
// click table button
// TODO:
$('#').on('click', buttonAction);

// --------------------------event handlers----------------------------
/**
* @desc display modal
* @param {event} event - click
*/
function buttonAction(event) {
  var data = {};
	// TODO: get app data from page
	data['appID'] = null;
	data['mcID'] = null;
  data['patient'] = null;
	data['date'] = null;
	data['time'] = null;
	data['doctor'] = null;
	data['symptoms'] = null;
  myModal.setMCID(data['mcID']);
  myModal.setApp(data);
  // request and fill in app status and comments
  myModal.loadAppInfo(data['appID']);
  // request and fill in medical record data
  myModal.loadMCInfo(data['mcID'], "patientViewAppt");
}
