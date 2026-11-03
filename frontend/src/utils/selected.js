// Each table's select-all only toggles its own rows, so collapsed groups
// on grouped list pages are never selected by accident.
function handleSelectAll(event) {
  const selectAll = event.target;
  const table = selectAll.closest("table");
  table.querySelectorAll('tbody input[name="entry_id"]').forEach((checkbox) => {
    checkbox.checked = selectAll.checked;
  });
}

function handleBtnVisibility() {
  const tables = document.querySelectorAll(".table-select");
  const deleteBtn = document.getElementById("delete-selected-btn");
  const markPaidBtn = document.getElementById("mark-paid-selected-btn");
  const archiveBtn = document.getElementById("archive-selected-btn");
  const unarchiveBtn = document.getElementById("unarchive-selected-btn");
  const htmlBtn = document.getElementById("html-selected-btn");
  const unhtmlBtn = document.getElementById("unhtml-selected-btn");
  const saveBtn = document.getElementById("save-selected-btn");

  tables.forEach((table) => {
    table.addEventListener("change", () => {
      const anyChecked = Array.from(
        document.querySelectorAll('.table-select tbody input[type="checkbox"]')
      ).some((checkbox) => checkbox.checked);

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
  });
}

document.querySelectorAll(".select-all").forEach((selectAll) => {
  selectAll.addEventListener("click", handleSelectAll);
});
handleBtnVisibility();
