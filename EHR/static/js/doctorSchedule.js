$(document).ready(function(){


		$('#search-date').datepicker({
			minDate: new Date()
		});
		
		$('.timepicker').timepicker({
		    timeFormat: 'h:mm p',
		    interval: 30,
		    minTime: '10',
		    maxTime: '6:00pm',
		    startTime: '10:00',
		    dynamic: false,
		    dropdown: true,
		    scrollbar: true,
		    zindex:999

		})

		$('#apply-btn').button();
		$('#create-slot').button();
		$('.do-btn').button();


})

//打开新增排版对话框
function openDialog(th){

		var height = $(window).height();
		var width = $(window).width();

		$('.create-slot-dialog').dialog({
			height:height * 0.6,
			width:width*0.6,
			title:'add slot',
			draggable:false,
			open:function(event,ui){
				$('#new-slot-date').datepicker({
					minDate: new Date()
				});
				$('#submit-btn').button();
				$('#clear').button();
			},
			close:function(event,ui){
				$('#new-slot-date').datepicker("destroy");
			}
		});

}

function submit(th){
	var data = getSlotInfo();
	$.ajax({
		url:"http://localhost:5000/newSlot",
		data:data,
		type:'POST',
		success:function(data){
			console.log(data);
		}
	})

}

function getSlotInfo(){
	var date = $('#new-slot-date').val();
	var startTime = $('#new-slot-time').val();
	var slotNumber = $('#new-slot-space').val();
	var data = {'date':date,'startTime':startTime,'slotNumber':slotNumber};
	return data;
}

function clearDate(th){
	console.log('hi');
	$('#new-slot-date').datepicker("setDate",null);
}

function openInfoDialog(){
	var height = $(window).height();
	var width = $(window).width();

	$('.warning-info').dialog({
		height:height * 0.15,
		width:width*0.15,
		draggable:false,
		position:{at:"right bottom"},
		show:{
			effect:"highlight",
			duration:1000
		}

	})
}