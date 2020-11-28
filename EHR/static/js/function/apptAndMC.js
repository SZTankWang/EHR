/**
* @author Jingyi Zhu
* @desc utilities for nurseViewAppt, nurseViewMC and doctorViewAppt
*/

// ---------------------capture user action--------------------------
// load lab report
// $(".lr-btn").on("click", loadLabReport);
// prevent default page refresh if lab report not loaded
$(".collapse").on("click", ".preview-btn", function(event){
  if ($(this).attr('href') == "") {
    event.preventDefault();
    alert("Lab report empty");
  }
})
// --------------------------event handlers----------------------------
/**
* @desc load lab report if the lab report card is clicked
* @this event target element - lab report card
*/
function loadLabReport() {
  const targetCard = $(this).attr("data-target");
  const button = $(targetCard+" a");
  if (button.attr('href') == ""){
    const lrID = button.attr('id').slice(6);
    const data = {"lrID": lrID};
    var updateHref = (res) => {
      if (res.file_path) {
        // button.attr('href', URL.createObjectURL(res.labReport));
        button.attr('href', res.file_path)
      }
    };
    sendRequest("nursePreviewLR", "POST", data, updateHref);
  }
}

//--------------------prescription and lab report card def---------------------
function newPrescriptionCard(index, idAndMedicine, dose, comments){
  var card = "<div class='card card-body'> <h5 class='mb-0'> <button class='btn btn-link' data-toggle='collapse' data-target='#pre" + index + "' aria-expanded='true' aria-controls='pre" + index + "'>" + idAndMedicine + "</button> </h5> <div id='pre" + index + "' class='collapse' aria-labelledby='pre" + index + "' data-parent='#prescriptions'> <div class='card-body'>" + dose + "</div> <div class='card-body'>" + comments + "</div> </div> </div>";
  return card
}

function newLabReportCard(index, type, id, comments, link){
  var card = "<div class='card card-body'> <h5 class='mb-0'> <button class='lr-btn btn btn-link' data-toggle='collapse' data-target='#lab" + index + "' aria-expanded='true' aria-controls='lab" + index + "'>" + index + ". " + type + "</button> </h5> <div id='lab" + index + "' class='collapse' aria-labelledby='lab" + index + "' data-parent='#labReports'> <hr> <div class='card-body'><span>Lab report id: " + id + " </span><a id='preview" + id + "' class='preview-btn btn btn-sm btn-outline-primary' href='" + link + "' target='_blank'>preview</a> </div> <div class='card-body'>" + comments + "</div> </div> </div>";
  return card
}
