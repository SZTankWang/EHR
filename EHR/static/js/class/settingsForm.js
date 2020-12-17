/**
* @author Jingyi Zhu
* @desc settings form wrappers
*/

/**
* @desc settings form for doctor, nurse and patient
*/
class Settings {
  constructor() {
    this.firstName = $("#firstName");
    this.lastName = $("#lastName");
    this.id = $("#id");
    this.email = $("#email");
    this.phone = $("#phone");
  }

  update(res) {
    this.firstName.val(res.firstName);
    this.lastName.val(res.lastName);
    this.id.val(res.id);
    this.email.val(res.email);
    this.phone.val(res.phone);
  }
}

/**
* @desc patient health info form
*/
class HealthInfo {
  constructor() {
    this.age = $("#age");
    this.gender = $("#gender");
    this.bloodType = $("#bloodType");
    this.allergies = $("#allergies");
    this.chronics = $("#chronics");
    this.medications = $("#medications");
  }

  update(res) {
    this.age.val(res.age);
    this.bloodType.val(res.bloodType);
    this.allergies.text(res.allergies);
    this.chronics.text(res.chronics);
    this.medications.text(res.medications);
    this.setGender(res.gender);
  }

  setGender(gender){
    var str = "option[value=" + gender + "]";
    $("#gender " + str).attr('selected','selected');
    this.state = $("#gender option:selected");
  }
}

/**
* @desc patient health info form that can switch between readonly and editable
* @page patientHealthInfo
*/
class DynamicHealthInfo extends HealthInfo {
  constructor() {
    super();
    this.button = $("#submitHealthInfo");
  }

  toggle(){
    this.toggleTarget(this.age);
    this.toggleTarget(this.bloodType);
    this.toggleTarget(this.allergies);
    this.toggleTarget(this.chronics);
    this.toggleTarget(this.medications);
    this.toggleTargetSelect(this.gender);
    this.toggleTargetDisable(this.button);
  }

  toggleTarget(target){
    target.toggleClass("form-control");
    target.toggleClass("form-control-plaintext");
    target.attr("readonly", function(index, attr){
      return attr == "readonly" ? null : "readonly";
    });
  }

  toggleTargetSelect(target){
    target.toggleClass("form-control");
    target.toggleClass("form-control-plaintext");
    this.toggleTargetDisable(target);
  }
  
  toggleTargetDisable(target){
    target.attr("disabled", function(index, attr){
      return attr == "disabled" ? null : "disabled";
    });
  }
}
