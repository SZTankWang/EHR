/**
* @author Jingyi Zhu
* @desc utilities for nurseViewAppt, nurseViewMC and doctorViewAppt
*/

// ---------------------capture user action--------------------------
// load lab report
// $(".preview-btn").on("click", loadLabReport);
// prevent default page refresh if lab report not loaded
// $(".collapse").on("click", ".preview-btn", function(event){
//   if ($(this).attr('href') == "") {
//     event.preventDefault();
//     alert("Lab report empty");
//   }
// })
// --------------------------event handlers----------------------------
/**
* @desc load lab report if the lab report card is clicked
* @this event target element - lab report card
*/
function loadLabReport(e) {
  const filename = $(e).attr('href');
  if (filename != ""){
    goToPageNewTab("previewOneLR/" + filename, 300);
  } else {
    alert("Lab report empty");
  }
}
// function loadLabReport(e) {
//   const targetCard = $(e).attr("data-target");
//   const button = $(targetCard+" a");
//   if (button.attr('href') == ""){
//     const lrID = button.attr('id').slice(6);
//     const data = {"lrID": lrID};
//     var updateHref = (res) => {
//       if (res.file_path) {
//         // button.attr('href', URL.createObjectURL(res.labReport));
//         button.attr('href', res.file_path)
//       }
//     };
//     sendRequest("nursePreviewLR", "POST", data, updateHref);
//   }
// }

//--------------------prescription and lab report card def---------------------
function newPrescriptionCard(index, idAndMedicine, dose, comments){
  var card = "<div class='card card-body'> <h5 class='mb-0'> <button class='btn btn-link' data-toggle='collapse' data-target='#pre" + index + "' aria-expanded='true' aria-controls='pre" + index + "'>" + idAndMedicine + "</button> </h5> <div id='pre" + index + "' class='collapse' aria-labelledby='pre" + index + "' data-parent='#prescriptions'> <div class='card-body'>" + dose + "</div> <div class='card-body'>" + comments + "</div> </div> </div>";
  return card;
}

function newLabReportCard(index, type, id, doctor_comments, nurse_comments, link){
  var card = "<div class='card card-body'> <h5 class='mb-0'> <button class='lr-btn btn btn-link' data-toggle='collapse' data-target='#lab" + index + "' aria-expanded='true' aria-controls='lab" + index + "'>" + index + ". " + type + "</button> </h5> <div id='lab" + index + "' class='collapse' aria-labelledby='lab" + index + "' data-parent='#labReports'> <hr> <div class='card-body'><span>Lab report id: " + id + " </span><button id='preview" + id + "' class='preview-btn btn btn-sm btn-outline-primary' href='" + link + "' target='_blank' onclick='loadLabReport(this)'>preview</button> </div> <div class='card-body'><span>Doctor's comments: </span><span>" + doctor_comments + "</span></div> <div class='card-body'><span>Nurse's comments: </span><span>" + nurse_comments + "</span></div> </div> </div>";
  return card;
}

//--------------------lab report request card def---------------------
function newLabReportReqCard(index, id, type, comments){
  var card = "<div class='card card-body'> <h5 class='mb-0'> <button class='btn btn-link' data-toggle='collapse' data-target='#req" + index + "' aria-expanded='true' aria-controls='req" + index + "'>" + id + ": " + type + "</button> </h5> <div id='req" + index + "' class='collapse' aria-labelledby='req" + index + "' data-parent='#labReportReqs'> <div class='card-body'> <form class='labReportForm' id='labReportForm" + index + "' enctype='multipart/form-data' onsubmit='return uploadLabReport(event)'> <div class='form-group row'> <label for='id' class='col-2 col-form-label'><b>Lab Report ID</b></label> <div class='col-5'> <input type='text' class='form-control-plaintext' id='labReportID" + index + "' name='id' value='" + id + "' readonly/> </div> </div> <div class='form-group row'> <span><b>Doctor's comments: </b>" + comments + "</span> </div> <div class='form-group row'> <label class='col-10 col-form-label' for='labReportInput'><b>Browse</b></label> <input class='form-control' type='file' id='labReportInput" + index + "' name='labReportInput' required> <label class='col-form-label' for='labReportInput'>supported file formats: .jpg, .png, .pdf</label> </div> <div class='form-group row'> <label class='col-10 col-form-label' for='commentsInput'><b>Comments</b></label> <textarea class='form-control' id='commentsInput" + index + "' name='commentsInput'></textarea> </div> <input type='submit' id='uploadReport" + index + "' class='btn btn-primary' value='Upload'/> </form> </div> </div> </div>";
  return card;
}
