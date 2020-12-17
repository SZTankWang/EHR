/**
* @author Jingyi Zhu
* @desc utilities for nurseViewAppt, nurseViewMC and doctorViewAppt
*/

// --------------------------event handlers----------------------------
/**
* @desc load lab report if the lab report card is clicked
* @param {element} e - lab report card
*/
function loadLabReport(e) {
  const filename = $(e).attr('href');
  if (filename != ""){
    goToPageNewTab("previewOneLR/" + filename, 300);
  } else {
    alert("Lab report empty");
  }
}

//--------------------card definitions---------------------
function newPrescriptionCard(index, id, medicine, dose, comments){
  var card = "<div class='card card-body'> <h5 class='mb-0'> <button class='btn btn-link' data-toggle='collapse' data-target='#pre" + id + "' aria-expanded='true' aria-controls='pre" + id + "'>" + index + ": " + medicine + "</button> </h5> <div id='pre" + id + "' class='collapse' aria-labelledby='pre" + id + "' data-parent='#prescriptions'> <div class='card-body'><span><b>Dose: </b>" + dose + "</span></div> <div class='card-body'><span><b>Comments: </b>" + comments + "</span></div> </div> </div>";
  return card;
}

function newLabReportCard(index, id, type, doctor_comments, nurse_comments, link){
  var card = "<div class='card card-body'> <h5 class='mb-0'> <button class='lr-btn btn btn-link' data-toggle='collapse' data-target='#lab" + id + "' aria-expanded='true' aria-controls='lab" + id + "'>" + "id " + id + ": " + type + "</button> </h5> <div id='lab" + id + "' class='collapse' aria-labelledby='lab" + id + "' data-parent='#labReports'> <hr> <div class='card-body'><span>Lab report id: " + id + " </span><button id='preview" + id + "' class='preview-btn btn btn-sm btn-outline-primary' href='" + link + "' target='_blank' onclick='loadLabReport(this)'>preview</button> </div> <div class='card-body'><span><b>Doctor's comments: </b></span><span>" + doctor_comments + "</span></div> <div class='card-body'><span><b>Nurse's comments: </b></span><span>" + nurse_comments + "</span></div> </div> </div>";
  return card;
}

function newLabReportReqCard(index, id, type, comments){
  var card = "<div class='card card-body'> <h5 class='mb-0'> <button class='btn btn-link' data-toggle='collapse' data-target='#req" + id + "' aria-expanded='true' aria-controls='req" + id + "'>" + "id " + id + ": " + type + "</button> </h5> <div id='req" + id + "' class='collapse' aria-labelledby='req" + id + "' data-parent='#labReportReqs'> <div class='card-body'> <form class='labReportForm' id='labReportForm" + id + "' enctype='multipart/form-data' onsubmit='return uploadLabReport(event)'> <div class='form-group row'> <label for='id' class='col-2 col-form-label'><b>Lab Report ID</b></label> <div class='col-5'> <input type='text' class='form-control-plaintext' id='labReportID" + index + "' name='id' value='" + id + "' readonly/> </div> </div> <div class='form-group row'> <span><b>Doctor's comments: </b>" + comments + "</span> </div> <div class='form-group row'> <label class='col-10 col-form-label' for='labReportInput'><b>Browse</b></label> <input class='form-control' type='file' id='labReportInput" + id + "' name='labReportInput' required> <label class='col-form-label' for='labReportInput'>supported file formats: .jpg, .png, .pdf</label> </div> <div class='form-group row'> <label class='col-10 col-form-label' for='commentsInput'><b>Comments</b></label> <textarea class='form-control' id='commentsInput" + id + "' name='commentsInput'></textarea> </div> <input type='submit' id='uploadReport" + id + "' class='btn btn-primary' value='Upload'/> </form> </div> </div> </div>";
  return card;
}
