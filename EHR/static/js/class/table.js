/**
* @author Jingyi Zhu
* @desc jQuery DataTable wrappers
*/

/**
* @desc basic table class
* @method updateTableData - empty the table and add new data
*/
class Table{
  constuctor(){
    this.table = null;
  }

  updateTableData(data){
    this.table.clear().draw();
    this.table.rows.add(data);
    this.table.columns.adjust().draw();
  }

  updateTable(data){
    this.updateTableData(data);
  }
}

/**
* @desc table for nurseHome and nurseAllAppt
* @method initTable - initialize the table
*/
class NurseTable extends Table{
  initTable(data){
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
          "defaultContent": "<button type='button' class='modal-button btn btn-sm btn-outline-primary'>View</button>"
      }]
    });
  }
}

/**
* @desc table for doctorHome and doctorAllAppt
* @method initTable - initialize the table
*/
class DoctorTable extends Table{
  initTable(data){
    this.table = $("#main-table").DataTable({
      "data": data,
      "columns" : [
          { "data" : "appID", "title": "Application ID" },
          { "data" : "date", "title": "Date" },
          { "data" : "time", "title": "Time" },
          { "data" : "patient", "title": "Patient" },
          { "data" : "symptoms", "title": "Symptoms" },
          { "data" : "status", "title": "Status" },
          { "data" : "", "title": "" }
      ],
      "columnDefs": [{
          "targets": -1,
          "orderable": false,
          "searchable": false,
          "data": null,
          "defaultContent": "<button type='button' class='modal-button btn btn-sm btn-outline-primary'>View</button>"
      }]
    });
  }
}

/**
* @desc table for medical records
* @method initTable - initialize the table
*/
class MCTable extends Table {
  initTable(data){
    this.table = $("#main-table").DataTable({
      "data": data,
      "columns" : [
          { "data" : "appID", "title": "Application ID" },
          { "data" : "mcID", "title": "Medical Record ID" },
          { "data" : "date", "title": "Date" },
          { "data" : "time", "title": "Time" },
          { "data" : "doctor", "title": "Doctor" },
          { "data" : "symptoms", "title": "Symptoms" },
          { "data" : "", "title": "" }
      ],
      "columnDefs": [{
          "targets": -1,
          "orderable": false,
          "searchable": false,
          "data": null,
          "defaultContent": "<button type='button' class='modal-button btn btn-sm btn-outline-primary' data-toggle='modal' data-target='#mc'>View</button>"
      }]
    });
  }

}
