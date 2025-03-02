var myModal = document.getElementById("hijackModal");
if (myModal) {
  myModal.addEventListener("show.bs.modal", function (event) {
    var button = event.relatedTarget;
    var userId = button.getAttribute("data-userid");
    var userName = button.getAttribute("data-username");
    var firstName = button.getAttribute("data-firstname");  // eslint-disable-line no-unused-vars
    var lastName = button.getAttribute("data-lastname");  // eslint-disable-line no-unused-vars
    var form = myModal.querySelector("#hijack-user");
    // Update form elements
    form.querySelector('input[name="user_pk"]').value = userId;

    // Update modal body
    var modalBody = myModal.querySelector(".modal-body");
    modalBody.innerHTML = "Hijack " + userName + "?";
  });
}
