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


