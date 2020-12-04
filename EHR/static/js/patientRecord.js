$(document).ready(function(){
	$('#apply').button();
	drawPagination();
})

function goBackHome(){
	window.location.replace('http://localhost:5000/loadHomePage');
}

function drawPagination(){
	var data = [];
	for (var i = 0; i<21; i++){
		data.push(i);
	}

	$('.pagination-container').pagination({
		pageSize:5,
		dataSource:'http://localhost:5000/getPatientRecord/', //replace this with url,
		showPrevious:true,
		showNext:true,
		ajax:{data:{type:'appointment'}},
		alias:{
			'pageNumber':'currPage'
		},
		callback: function(data, pagination) {
        // template method of yourself
        var html = renderCard(data);
        $('.card-list.container').html(html);
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



