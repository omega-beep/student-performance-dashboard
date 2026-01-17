// ---------- GLOBAL STATE ----------
let allStudents = [];
let marksChart = null;
let statusChart = null;

// ---------- ADD STUDENT ----------
function addStudent() {
    const name = document.getElementById('name').value;
    const marks = document.getElementById('marks').value;
    const attendance = document.getElementById('attendance').value;

    fetch('/add_student', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, marks, attendance })
    })
    .then(() => loadStudents())
    .then(() => clearInputs());
}

// ---------- LOAD FROM BACKEND ----------
function loadStudents() {
    fetch('/students')
        .then(res => res.json())
        .then(data => {
            allStudents = data;
            applyFilters();
        });
}

// ---------- SEARCH & FILTER ----------
function applyFilters() {
    const searchEl = document.getElementById('searchInput');
    const gradeEl = document.getElementById('gradeFilter');

    // Safety check (prevents crash)
    if (!searchEl || !gradeEl) {
        console.log("Search or filter input not found yet");
        renderStudents(allStudents);
        return;
    }

    const searchText = searchEl.value.toLowerCase();
    const selectedGrade = gradeEl.value;

    const filtered = allStudents.filter(student => {
        const matchesName = student.name.toLowerCase().includes(searchText);
        const matchesGrade =
            selectedGrade === "All" || student.grade === selectedGrade;

        return matchesName && matchesGrade;
    });

    renderStudents(filtered);
}


// ---------- RENDER LIST + CHARTS ----------
function renderStudents(data) {
    const list = document.getElementById('studentList');
    list.innerHTML = "";

    let names = [];
    let marks = [];
    let passCount = 0;
    let failCount = 0;

    data.forEach(student => {
        const item = document.createElement('li');
        item.innerHTML = `
            ${student.name} | Marks: ${student.marks} | Attendance: ${student.attendance}%
            | Status: ${student.status} | Grade: ${student.grade}
            <button onclick="deleteStudent(${student.id})">Delete</button>
        `;
        list.appendChild(item);

        names.push(student.name);
        marks.push(student.marks);

        if (student.status === "Pass") passCount++;
        else failCount++;
    });

    drawMarksChart(names, marks);
    drawStatusChart(passCount, failCount);
}

// ---------- DELETE ----------
function deleteStudent(id) {
    fetch(`/delete_student/${id}`, { method: 'DELETE' })
        .then(() => loadStudents());
}

// ---------- CHARTS ----------
function drawMarksChart(names, marks) {
    const canvas = document.getElementById('marksChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    if (marksChart) marksChart.destroy();

    marksChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: names,
            datasets: [{
                label: 'Marks',
                data: marks,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

function drawStatusChart(passCount, failCount) {
    const canvas = document.getElementById('statusChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    if (statusChart) statusChart.destroy();

    statusChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Pass', 'Fail'],
            datasets: [{
                data: [passCount, failCount]
            }]
        },
        options: { responsive: true }
    });
}

// ---------- UTILS ----------
function clearInputs() {
    document.getElementById('name').value = "";
    document.getElementById('marks').value = "";
    document.getElementById('attendance').value = "";
}

// ---------- START ----------
loadStudents();
