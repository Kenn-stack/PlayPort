const selectAll = document.getElementById('select-all');
  const checkboxes = document.querySelectorAll('.item-checkbox');

  seletAll.addEventListener('change', () => {
    checkboxes.forEach(checkbox => {
      checkbox.checked = selectAll.checked;
    });
  });

  // Optional: update "select all" if individual boxes change
  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', () => {
      const allChecked = Array.from(checkboxes).every(c => c.checked);
      selectAll.checked = allChecked;
    });
