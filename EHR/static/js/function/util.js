/**
* @author Jingyi Zhu
* @desc utilities
*/

function goToPage(route, delay){
  setTimeout("window.location.replace('http://localhost:5000/" + route + "')", delay);
}

function jsonify(data){
  var obj = {};
  for(var i=0;i<data.length;i++){
    obj[data[i].name]=data[i].value;
  }
  return obj;
}

function sendRequest(route, type, data, successHandler){
  $.ajax({
    url: "http://localhost:5000/" + route,
    type: type,
    data: data,
    success: (res) => {
      successHandler(res);
    },
    error: (err) => {
      alert("request error");
      console.log(err);
      $("#overlay").addClass("d-none");
    }
  });
}

function getFullDate(date){
  return date.toISOString().split("T")[0];
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
