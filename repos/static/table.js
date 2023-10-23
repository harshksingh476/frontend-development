// Sample data
const data = [
  { id: 1, name: 'Alice', age: 28 },
  { id: 2, name: 'Bob', age: 32 },
  { id: 3, name: 'Charlie', age: 25 },
  // ... more data
];

// Function to populate the table
function populateTable() {
  const tableBody = document.querySelector('#data-table tbody');

  data.forEach(rowData => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${rowData.id}</td>
      <td>${rowData.name}</td>
      <td>${rowData.age}</td>
    `;
    tableBody.appendChild(row);
  });
}

// Call the populateTable function when the page loads
window.addEventListener('load', populateTable);
