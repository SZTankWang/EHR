/**
* @desc jQuery DataTable wrapper
* @method initTable - initialize the table
* @method updateTable - empty the table and add new data
*/
class HomeTable {
  constructor(){
    this.table = null;
  }

  initTable(data, btnTarget){
    this.table = $("#main-table").DataTable({
      "data": data,
      "columns" : [
          { "data" : "appID", "title": "Application ID" },
          { "data" : "date", "title": "Date" },
          { "data" : "time", "title": "Time" },
          { "data" : "doctor", "title": "Doctor" },
          { "data" : "patient", "title": "Patient" },
          { "data" : "symptoms", "title": "Symptoms" },
          { "data" : "", "title": "" }
          // , "render": (data, type, row, meta) => `<button type="button" class="modal-button btn btn-outline-primary" data-toggle="modal" data-target="#application">View</button>`
      ],
      "columnDefs": [{
          "targets": -1,
          "orderable": false,
          "searchable": false,
          "data": null,
          "defaultContent": "<button type='button' class='modal-button btn btn-outline-primary' data-toggle='modal' data-target='#" + btnTarget + "'>View</button>"
      }]
    });
  }

  updateTable(data, btnTarget){
    this.table.clear().draw();
    this.table.rows.add(data);
    this.table.columns.adjust().draw();
    $(".modal-button").each(function(){
      $(this).attr('data-target',btnTarget);
    });
  }
}

class HomeModal {
  constructor(){
    this.appID = $("#appID");
    this.date = $("#date");
    this.time = $("#time");
    this.doctor = $("#doctor");
    this.patient = $("#patient");
    this.symptoms = $("#symptoms");
  }

  update(data){
    this.appID.text(data['appID']);
    this.date.text(data['date']);
    this.time.text(data['time']);
    this.doctor.text(data['doctor']);
    this.patient.text(data['patient']);
    this.symptoms.text(data['symptoms']);
  }
}
