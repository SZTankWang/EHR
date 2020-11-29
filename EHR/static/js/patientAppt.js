	$(document).ready(function(){
	//页面初始加载后，获取第一个科室的ID
	$('.dept-btn').each(function(){
		if($(this).hasClass('active')){
			var deptID = $(this).attr('id');
			loadDoctorByDept(deptID);
		}
	})



	/*监听 点击科室 切换科室
	*/
	//去除点击前active 的按钮样式, 点击的元素添加样式
	$('.dept-btn').click(function(){
		console.log('click');
		$(this).parent().children('.dept-btn').each(function(){
			if($(this).hasClass('active')){
				$(this).removeClass('active');
			}


		})
		$(this).addClass('active');
		$('#currDeptName').val($(this).text());
		// console.log($(this).text());
		var dept = $(this).text();
		console.log(dept);
		var deptID = $(this).attr("id");
		console.log(deptID);
		loadDoctorByDept(deptID);
		// loadDoctorByDept()
		// var hospitalID = 
		// ajax请求
		// $.ajax({
		// 	url:"http://localhost:5000/loadDoctorByDept",
		// 	data:{'dept':}

		// })

		})



	})


	function getActiveDept(){
		$('.dept-btn').each(function(){
			if($(this).hasClass('active')){
				var selectDept = $(this).attr('id');
				console.log(selectDept);
				loadDoctorByDept(selectDept);
			}
		})
	}


	/*
		根据选中科室ID加载医生列表

	*/
	function loadDoctorByDept(deptID){
		$.ajax({
			url:"http://localhost:5000/getDoctorByDept",
			data:{'deptID':deptID},
			success:function(data){
				console.log(data);
				$('#card-list').empty();
				for(var i=0;i<data.length;i++){
					$('#card-list').append(renderDoctor(data[i]));
				}
			}

		})


	}

	//绘制医生列表
	function renderDoctor(doctor){
		var temp = '';
		temp += '<div class="row w-100"><div class="col"><div class="card"><div class="card-body"><div class="row w-100"><div class="doctor-avatar col-md-2"><svg width="4em" height="4em" viewBox="0 0 16 16" class="bi bi-circle" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/></svg></div><div class="card-text col-md-6"><p>Dr.&nbsp'+doctor['doctorName']+'</p>';
		temp += '<p>'+doctor['hospital']+' '+doctor['department']+'</p></div><a href="#" class="btn btn-primary col-md-2 offset-md-2 appoint-button" onclick="createDocFrame(this)" id='+doctor['doctorID']+'>Appoint</a></div></div></div></div>'
		return temp;
	}


	// 创建预约医生Iframe
	function createDocFrame(th){
		//清除card list
		$('#card-list').empty();

		var doctorID = $(th).attr("id");
		console.log(doctorID);
		var frame = document.createElement('iframe');
		frame.setAttribute('id',doctorID);
		frame.setAttribute('style','width:100%;height:100%;overflow-x:hidden;');
		frame.setAttribute('scrolling','yes');
		frame.setAttribute('frameBorder',0);
		$('#card-list').append(frame);
		frame.setAttribute('src','http://localhost:5000/viewDoctor/'+doctorID);

		//返回栏设置为可见
		document.getElementById("close-frame-container").style.display="block";
	}


	// 打开模态框
	function openModal(th){
		console.log($(th).attr('id'));
		var slotID = $(th).attr('id');
		//设定提交按钮id
		$('.submit-btn').attr('id',slotID);

		//请求slot 信息
		getSlotInfo(slotID);

		var width=$(window).width();
		var height = $(window).height();
		$('.book-dialog').dialog({
			width:width*0.6,
			height:height*0.7,
			draggable:false


		});
	}

	// 根据日期获取排班
	function getDocSlot(date){
		var doctorID = $('#doctorID').val();
		$.ajax({
			url:"http://localhost:5000/getDoctorSlot",
			data:{
				'date':date,
				'doctorID':doctorID
					},
			success:function(data){
				$('#time-slot-list').empty();
				console.log(data);
				for(var i=0;i<data.length;i++){
					renderTimeSlot(data[i]);
				}
				$('.book-btn').button();
			}
		})
	}


	function renderTimeSlot(data){
		var temp = '<!-- 单个时间段 --><li id='+data['slotID']+'><div class="time-slot-row"><div class="time-slot-info time"><h4>'+data['slotTime']+'</h4></div><div class="wrapper"><div class="time-slot-info availSpace">Available Space: '+data['avail_num']+'</div><div class="time-slot-info reserve"><button class="book-btn" id='+data['slotID']+' onclick="openModal(this)" data-toggle="modal" data-target="#myModal">make an appointment</button></div></div></div></li>';
		
		$('#time-slot-list').append(temp);
	}

	
	//点击返回 返回到医生列表
	function closeFrame(){
		$('#card-list').empty();
		document.getElementById('close-frame-container').style.display='none';
		getActiveDept();
	}


	// 根据用户输入时间 查询可用slot
	function searchSlotByDate(){
		var date = $('#select-date').datepicker("getDate");
		date = moment(date).format("YYYY-MM-DD");
		console.log(date);
		getDocSlot(date);
	}

	function submitAppt(th){
		console.log($(th).attr('id'));
		var slotID = $(th).attr('id');
		var doctorID = $('#doctorID').val();
		info = getApptInfo(slotID,doctorID);
		$.ajax({
			url:"http://localhost:5000/makeAppt",
			data: info,
			type:'POST',
			success:function(data){
				console.log(data);
			}
		})
	}

	//获取预约信息
	function getApptInfo(slotID,doctorID){
		var name = $('#appt-name').val();
		var phone = $('#appt-phone').val();
		var synopsis = $('#synopsis').val();

		var info = {};
		info['slotID'] = slotID;
		info['doctorID'] = doctorID;
		info['name'] = name;
		info['phone'] = phone;
		info['symptom']=synopsis;

		return info;

	}


	function getSlotInfo(slotID){
		$.ajax({
			url:"http://localhost:5000/querySlotInfo",
			data:{'slotID':slotID},
			type:'GET',
			success:function(data){
				console.log(data);
			}
		})


	}