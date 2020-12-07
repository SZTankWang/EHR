$(document).ready(function(){

	renderNotice();
})




function goToAppointment(){
	window.location.replace('http://localhost:5000/hospitalListPage');
}


function goToRecord(){
	window.location.replace('http://localhost:5000/patientRecord');
}


//添加近期预约
function renderNotice(){
	//测试数据
	var arr = new Array();
	var date = new Date();

	//console.log(date);
	$.ajax({
		url:"http://localhost:5000/patientFutureAppt",
		data:{'currPage':1,'pageSize':3},
		type:"GET",
		success:function(data){
			console.log(data);
			for(var i=0;i<data['apps'].length;i++){
				html = apptTemplate(data['apps'][i])
				$("#outer-container").append(html);
				var id = data['apps'][i]['appID']
			}
		}
	})


function apptTemplate(data){
		var temp ='';
		temp +='<div class="recent"><div class="time">'+data['date']+'</div>';
		temp +='<div class="info"><div class="info-content">'+data['hospital']+'</div>';
		temp += '<div class="info-content">'+data['department']+'</div>'
		temp += '<div class="info-content">'+data['doctor']+'</div><div class="info-content">'+data['time']+'</div>';
		return temp;
}

	//拼接notice
	for(var i=0;i<arr.length;i++){

		var id=arr[i].id;
		var state=arr[i].state;
		renderState(state,id);
	}
}
//根据预约状态渲染状态 div 颜色
function renderState(state,id){
	if(state=='upcoming'){
		document.getElementById(id).style.background='#53AD06';
	}
	else{
		document.getElementById(id).style.background='#AEB6BF';
	}
}
