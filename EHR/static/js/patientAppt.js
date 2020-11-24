	$(document).ready(function(){
	/*监听 点击科室 切换科室
	

	*/
	//去除点击前active 的按钮样式, 点击的元素添加样式
	$('.hospital-btn').click(function(){
		console.log('click');
		$(this).parent().children('.hospital-btn').each(function(){
			if($(this).hasClass('active')){
				$(this).removeClass('active');
			}


		})
		$(this).addClass('active');
		$('#currDeptName').val($(this).text());
		// console.log($(this).text());
		var dept = $(this).text();
		console.log(dept);
		// var hospitalID = 
		// ajax请求
		// $.ajax({
		// 	url:"http://localhost:5000/loadDoctorByDept",
		// 	data:{'dept':}

		// })

		})

	})


	/*
		根据选中科室ID加载医生列表

	*/
	function loadDoctorByDept(deptID){
		$.ajax({
			url:"http://localhost:5000/getDoctorByDept",
			data:{'deptID':deptID},
			success:function(data){
				console.log(data);
			}

		})


	}

	function renderDoctor(data){
		
	}

'<div class="row w-100"><div class="col"><div class="card"><div class="card-body"><div class="row w-100"><div class="doctor-avatar col-md-2"><svg width="4em" height="4em" viewBox="0 0 16 16" class="bi bi-circle" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/></svg></div><div class="card-text col-md-6"><p>Dr.John Smith</p><p>Oriental Hospital  Emergency Department</p></div><a href="#" class="btn btn-primary col-md-2 offset-md-2 appoint-button">Appoint</a></div></div></div></div>'