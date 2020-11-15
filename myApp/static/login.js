// $(document).ready(function(){
// 		renderFormType();
// 		goRegister();
// 		goLogin();
// 		if($('.choice-btn-container').length>0){
// 			detectChoice();
// 		}


//登录页头登录/注册切换按钮
function renderFormType(){
	var type=$('.form').attr('id');
	if(type=='login-form'){
		$('#go-login').css({'background':'#2D79D6','color':'white' 	});
	}
	else{
		$('#go-register').css({'background':'#2D79D6','color':'white'});
	}
	
}

function goRegister(){
	$("#go-register").click(function(){
		// console.log('点击注册');
		if($('.form').attr('id')=='login-form'){
			console.log('切换至注册');
			$(this).css({'background':'#2D79D6','color':'white'});
			$('#go-login').css({'background':'white','color':'#BCC3CA'});
			//用户选择注册角色
			//先清空表单
			clear();	
			$('#login-field').append(renderChoice());
		}
	})
}

function detectChoice(){
	if($('.choice-btn-container').length>0){
		$('.choice-btn-container').click(function(){
			console.log('点击');
			if($(this).attr('id')=='doctor'){
				console.log('选择医生');
				//渲染医生登录表单
				}
			if($(this).attr('id')=='staff'){
				console.log('选择护士');
				//护士登录表单
			}
			if($(this).attr('id')=='patient'){
				console.log('选择病人');
				//病人登录表单
				//首先清空
				$('#choice-view-container').remove();
			}
			})
	}
	// document.getElementById('doctor').onclick=function(){console.log('test')};

}

function clickDoctor(){
	console.log('捕捉');
}

//清空表单和忘记密码
function clear(){
	$('.form').remove();
	$('#login-btn-wrapper').remove();
	$('#option-container').remove();
}

//替换成选择角色
function renderChoice(){
	var temp="";
	temp+= "<!-- 按钮部分 --><div id='choice-view-container'><div id='choice-header-wrapper'><div id='choice-header'>Register as:</div><span></span></div><div id='choice-btn-outer-container'><div class='choice-btn-container' id='doctor' onclick='clickDoctor()'><div class='choice-background' id='doctor-background'></div><div class='choice-description'>Doctor</div></div><div class='choice-btn-container' id='staff' onclick='clickNurse()'><div class='choice-background' id='staff-background'></div><div class='choice-description'>Staff</div></div><div class='choice-btn-container' id='patient' onclick='clickPatient()'><div class='choice-background' id='patient-background'></div><div class='choice-description'>Patient</div></div></div></div>";
	return temp;
}

function renderRegister(){
	$('.form').attr('id','register-form');
	$('.form').empty();
	$('.form').append(concatRegister());

}

function concatRegister(){
	var temp = '';
	temp += '<div class="register-input" ><label for="legalName">User</label><input type="text" id="legalName"></div><div class="register-input"><label for="ID">ID</label><input type="text" id="ID"></div><div class="register-input"><label for="phone">Phone</label><input type="text" id="phone"></div><div class="register-input"><label for="Email">Email</label><input type="text" id="Email"></div><div class="register-input"><label for="username">Username</label><input type="text" id="username"></div><div class="register-input"><label for="password">Password</label><input type="text" id="password"></div>';
	return temp;
}

function concatLogin(){
	var temp='';
	temp += '<form action="" class="form" id="login-form"><div class="login-input" id="input-name" ><label for="username">User</label><input type="text" id="login-username"></div><div class="login-input" id="login-input-pass"><label for="password">Password</label><input type="text" id="password"></div></form>';
	temp+= '<div id="login-btn-wrapper"><button type="button" class="primary-btn" id="doLogin">Login</button></div>';			

	temp+='<div id="option-container"><div class="login-option" id="forget-password">forget password</div><div class="login-option" id="forget-username">forget username</div></div>';

	return temp;
}

function goLogin(){
	$('#go-login').click(function(){
		// console.log('点击登录');
		if($('form').attr('id')!='login-form'){
			console.log('切换至登录');
			$('#go-login').css({'background':'#2D79D6','color':'white'});
			$('#go-register').css({'background':'white','color':'rgb(188,195,202)'});
			if($('#choice-view-container')){
				$('#choice-view-container').remove();
			}
			// $('.form').empty();
			// $('.form').attr('id','')
			$('#login-field').append(concatLogin());
		}
	})
}

function renderLoginForm(){

}


export {goRegister,renderFormType};

				

					
					


			
				
					
				
				
					
				
			
