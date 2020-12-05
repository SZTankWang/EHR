$(document).ready(function(){


		$('#search-date').datepicker({
			minDate: new Date()
		});

		$('.timepicker').timepicker({
		    timeFormat: 'HH:mm',
		    interval: 60,
		    minTime: '10',
		    maxTime: '18:00',
		    startTime: '10:00',
		    dynamic: false,
		    dropdown: true,
		    scrollbar: true,
		    zindex:999

		})

		$('#apply-btn').button();
		$('#create-slot').button();
		$('.do-btn').button();

		sendRequest("doctorGetSlots", "GET", null, setCalendar);

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
		url:"http://localhost:5000/doctorNewSlot",
		data:data,
		type:'POST',
		success:function(data){
			console.log(data);
			if (data['ret'] == 0 ) {
				openInfoDialog('success');
				setTimeout(function(){
					$('.create-slot-dialog').dialog("destroy");
				},1000);

				var date = $('#new-slot-date').val("");
				var startTime = $('#new-slot-time').val("");
				var slotNumber = $('#new-slot-space').val("");

				sendRequest("doctorGetSlots", "GET", null, setCalendar);

				setTimeout(function(){
					$('.success-info').dialog('destroy');
				},2500);
			} else {
				openInfoDialog('failure');

				setTimeout(function(){
					$('.failure-info').dialog('destroy');
				},2500);

			}
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

function openInfoDialog(type){
	var height = $(window).height();
	var width = $(window).width();

	if(type == "success"){
		$('.success-info').dialog({
			height:height * 0.20,
			width:width*0.20,
			draggable:false,
			position:{at:"right bottom"},
			show:{
				effect:"highlight",
				duration:1000
			}

		})
	}

	if(type == "failure"){
		$('.warning-info').dialog({
			height:height * 0.20,
			width:width*0.20,
			draggable:false,
			position:{at:"right bottom"},
			show:{
				effect:"highlight",
				duration:1000
			}

		})
	

	}

}


function setCalendar(res) {
	var calendarEl = document.getElementById('calendar');
	console.log(calendarEl);
	var calendar = new FullCalendar.Calendar(calendarEl, {
		eventClick: function() {
			// alert('an event has been clicked!');
		},

		slotMinTime: "07:00:00",
		slotMaxTime: "20:00:00",
		initialView: 'timeGridWeek',
		initialDate: getFullDate(new Date()),
		headerToolbar: {
			left: 'prev,next today',
			center: 'title',
			right: 'dayGridMonth,timeGridWeek,timeGridDay'
		},
		events: res.data,
	});
	calendar.render();
}
