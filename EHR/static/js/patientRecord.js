
$(document).ready(function(){
	$('#apply').button();
	drawPagination();

	$('.link').click(function(){
		console.log('hi');
	});
})

function goBackHome(){
	window.location.replace('http://localhost:5000/loadHomePage');
}

function drawPagination(){
	// var data = $.ajax({
	// 	url:'http://localhost:5000/getPatientRecord',
	// 	data:''
	// })

	var pageType = $('#pageType');

	$('.pagination-container').pagination({
		pageSize:5,
		dataSource:'http://localhost:5000/getPatientRecord',
		locator:'apps',
		totalNumberLocator:function(response){
			return response.total_number;
		},
		showPrevious:true,
		showNext:true,
		ajax:{data:{type:pageType}},
		alias:{
			'pageNumber':'currPage'
		},
		callback: function(data, pagination) {
        // template method of yourself
        	console.log(data);
        	//set total number
        	$('#total_count').empty();
        	$('#total_count').html(data.length);
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
	temp += '</p></div></div><div class="my-container card-row"><div class="my-container text-wrapper"><p>time&nbsp&nbsp';
	temp += data['date']+'  ' +data['time'];
	temp += '</p></div></div>';
	temp += '<div class="my-container status pending"><div class="my-container"><p>';
	temp += data['status'];
	temp += '</p></div></div></div>';

	return temp;



}
