/**
* @author Jingyi Zhu
* @desc utilities
*/

function jsonify(data) {
  var obj = {};
  for(var i=0;i<data.length;i++){
    obj[data[i].name]=data[i].value;
  }
  return obj;
}

function goToPage(route, delay) {
  setTimeout("window.location.replace('http://localhost:5000/" + route + "')", delay);
}

function goBackHome(){
  goToPage("loadHomePage", 0);
}

function goToPageNewTab(route, delay) {
  setTimeout("window.open('http://localhost:5000/" + route + "')", delay);
}

function sendRequest(route, type, data, successHandler){
  $("#overlay").removeClass("d-none");
  $.ajax({
    url: "http://localhost:5000/" + route,
    type: type,
    data: data,
    success: (res) => {
      successHandler(res);
      $("#overlay").addClass("d-none");
    },
    error: (err) => {
      alert("request error");
      console.log(err);
      $("#overlay").addClass("d-none");
    }
  });
}

function getFullDate(date) {
  return date.toISOString().split("T")[0];
}

function getFullTime(date) {
  return date.toISOString().split("T")[1];
}

//-----------------------allAppt page-----------------------
function getRoute(role){
  if ($(".nav-table.active").text() == "Ongoing appointments") {
    return role + "OnGoingAppt";
  } else if ($(".nav-table.active").text() == "Future appointments") {
    return role + "FutureAppt";
  } else if ($(".nav-table.active").text() == "Past appointments") {
    return role + "PastAppt";
  } else {
    return role + "RejectedApp";
  }
}

function switchInputAttr (start, end, startRequired, endRequired, startDate, endDate, minDate, maxDate, submit) {
  $("#startDate").prop("readonly", start);
  $("#endDate").prop("readonly", end);
  $("#startDate").prop("required", startRequired);
  $("#endDate").prop("required", endRequired);
  $("#startDate").prop("value", startDate);
  $("#endDate").prop("value", endDate);
  $("#startDate").attr('min', minDate);
  $("#startDate").attr('max', maxDate);
  $("#endDate").attr('min', minDate);
  $("#endDate").attr('max', maxDate);
  $("#applyRange").prop("disabled", submit);
}

function setStartOrEndDate(startDate=null, endDate=null) {
  var today = getFullDate(new Date());
  if (!startDate && !endDate) {
    startDate = today;
  }
  if ($(".nav-table.active").text() == "Ongoing appointments") {
    switchInputAttr (true, true, false, false, startDate, startDate, "", "", true);
  } else if ($(".nav-table.active").text() == "Future appointments") {
    switchInputAttr (false, false, true, false, startDate, endDate, today, "", false);
  } else if ($(".nav-table.active").text() == "Past appointments") {
    switchInputAttr (false, false, false, true, startDate, endDate, "", today, false);
  } else {
    switchInputAttr (false, false, false, false, startDate, endDate, "", "", false);
  }
}

function jsonifyDateRange(startDate, endDate, range=0) {
  if (range < 0) {
    startDate.setDate(endDate.getDate() + range);
  } else if (range > 0) {
    endDate.setDate(startDate.getDate() + range);
  }

  var startDateStr = getFullDate(startDate);
  var endDateStr = getFullDate(endDate);
  var dateRange = {"startDate": startDateStr, "endDate": endDateStr};
  return dateRange;
}

//-------------------------tab styling--------------------------
// main navigation
$(".nav-main").on("click", function(event) {
    var clickedItem = $(this);
    $(".nav-main").each( function() {
      if ($(this).hasClass("active disabled")) {
        $(this).removeClass("active disabled");
      }
    });
    clickedItem.addClass("active disabled");
});

// table navigation
$(".nav-table").on("click", function(event) {
    var clickedItem = $(this);
    $(".nav-table").each( function() {
        if ($(this).hasClass("active disabled")) {
          $(this).removeClass("active disabled");
        }
    });
    clickedItem.addClass("active disabled");
});
