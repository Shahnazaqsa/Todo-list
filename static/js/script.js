document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('searchInput');
  const todoItems = document.querySelectorAll('.todo-item');

  // Search/filter todos
  searchInput.addEventListener('input', () => {
    const filter = searchInput.value.toLowerCase();
    todoItems.forEach(item => {
      const title = item.getAttribute('data-title').toLowerCase();
      const desc = item.getAttribute('data-desc').toLowerCase();
      if (title.includes(filter) || desc.includes(filter)) {
        item.style.display = '';
      } else {
        item.style.display = 'none';
      }
    });
  });

  // Mark todo as done toggle
  const markDoneCheckboxes = document.querySelectorAll('.mark-done');
  markDoneCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', (e) => {
      const todoItem = e.target.closest('.todo-item');
      if (e.target.checked) {
        todoItem.classList.add('done');
      } else {
        todoItem.classList.remove('done');
      }
      // Optionally, send update to backend here if supported
    });
  });

  // Confirmation for delete
  const deleteLinks = document.querySelectorAll('.delete-todo');
  deleteLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const confirmed = confirm('Are you sure you want to delete this todo?');
      if (!confirmed) {
        e.preventDefault();
      }
    });
  });
});


  var typed = new Typed("#typed", {
    strings: [
      "Plan your day with focus",
      "Track your todos like a pro",
      "Stay organized, stay sharp"
    ],
    typeSpeed: 50,
    backSpeed: 30,
    loop: true
  });



  

