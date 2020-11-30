/**
* @author Jingyi Zhu
* @desc settings form wrappers
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
