$(document).ready(function(){

	renderNotice();
})




function goToAppointment(){
	window.location.replace('http://localhost:5000/hospitalListPage');
}




//添加近期预约
function renderNotice(data){
	//测试数据
	var arr = new Array();
	var date = new Date();

	//console.log(date);
	arr.push({'id':1,'time':date,'hospital':'hospital','dept':'department','doctor':'doctor','state':'upcoming'});
	arr.push({'id':2,'time':date,'hospital':'hospital','dept':'department','doctor':'doctor','state':'upcoming'});
	arr.push({'id':3,'time':date,'hospital':'hospital','dept':'department','doctor':'doctor','state':'finished'});

	//拼接notice
	for(var i=0;i<arr.length;i++){
		var temp ='';
		temp +='<div class="recent"><div class="time">'+arr[i].time+'</div>';
		console.log(arr[i].time);
		temp +='<div class="info"><div class="info-content">'+arr[i].hospital+'</div>';
		temp += '<div class="info-content">'+arr[i].dept+'</div><div class="info-content">'+arr[i].doctor+'</div><div class="info-content" id='+arr[i].id+'>'+arr[i].state+'</div>';
		$("#outer-container").append(temp);

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
