function handleSelectAll() {
  var selectAll = document.getElementById("select-all");
  var checkboxes = document.getElementsByName("entry_id");
  checkboxes.forEach(function (checkbox) {
    checkbox.checked = selectAll.checked;
  });
}

function handleBtnVisibility() {
  const table = document.getElementById("table-select");
  const deleteBtn = document.getElementById("delete-selected-btn");
  const markPaidBtn = document.getElementById("mark-paid-selected-btn");
  const archiveBtn = document.getElementById("archive-selected-btn");
  const unarchiveBtn = document.getElementById("unarchive-selected-btn");
  const htmlBtn = document.getElementById("html-selected-btn");
  const unhtmlBtn = document.getElementById("unhtml-selected-btn");
  const saveBtn = document.getElementById("save-selected-btn");

  if (table) {
    table.addEventListener("change", () => {
      const checkboxes = table.querySelectorAll('tbody input[type="checkbox"]');
      const anyChecked = Array.from(checkboxes).some(
        (checkbox) => checkbox.checked
      );

      const buttons = [
        deleteBtn,
        markPaidBtn,
        archiveBtn,
        unarchiveBtn,
        htmlBtn,
        unhtmlBtn,
        saveBtn,
      ];
      buttons.forEach((btn) => {
        if (btn) {
          btn.style.display = anyChecked ? "block" : "none";
        }
      });
    });
  }
}

var selectAll = document.getElementById("select-all");
if (selectAll) {
  selectAll.addEventListener("click", handleSelectAll);
}
handleBtnVisibility();
