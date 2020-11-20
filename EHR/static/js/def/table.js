/**
* @author: Jingyi
* @desc jQuery DataTable wrappers
* @method initTable - initialize the table
* @method updateTableData - empty the table and add new data
* @method updateTable - update table data and other features
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
}

class HomeTable extends Table{
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
          "defaultContent": "<button type='button' class='modal-button btn btn-sm btn-outline-primary' data-toggle='modal' data-target='#" + btnTarget + "'>View</button>"
      }]
    });
  }

  updateTable(data, btnTarget){
    this.updateTableData(data);
    $(".modal-button").each(function(){
      $(this).attr('data-target',btnTarget);
    });
  }
}

class MCTable extends Table {
  initTable(data){
    console.log("hiiii");
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

  updateTable(data){
    this.updateTableData(data);
  }
}
