import json
import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

# Initialize Flask app
app = Flask(__name__)

# Define data file path
DATA_FILE = 'planner_data.json'

# --- Data Persistence Functions ---
def load_data():
    """Loads planner data from the JSON file. Creates an empty file if it doesn't exist or is empty."""
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        save_data({'tasks': [], 'subjects': [], 'journal': {}})
        return {'tasks': [], 'subjects': [], 'journal': {}}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    """Saves planner data to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- Main App Route ---
@app.route('/')
def index():
    """Renders the single-page planner application."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Smart Study Planner</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #a8c0ff, #3f2b96);
        }
        .container {
            min-height: 100vh;
        }
        .card {
            background-color: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
        }
        input[type="date"]::-webkit-calendar-picker-indicator {
            filter: invert(1);
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .tab-button.active {
            background-color: rgba(255, 255, 255, 0.9);
            color: #3f2b96;
            font-weight: 600;
        }
        .task-item {
            transition: all 0.3s ease-in-out;
        }
        .task-completed {
            text-decoration: line-through;
            color: #888;
        }
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 2px;
        }
        .calendar-day {
            min-height: 120px;
            padding: 8px;
            background-color: #f7f7f7;
            border-radius: 8px;
            overflow: hidden;
            position: relative;
        }
        .calendar-day.current-month {
            background-color: #fff;
        }
        .calendar-day .tasks {
            list-style: none;
            padding: 0;
            margin-top: 4px;
        }
        .calendar-day .task-entry {
            font-size: 0.75rem;
            line-height: 1.25;
            padding: 2px 4px;
            border-radius: 4px;
            margin-bottom: 2px;
            background-color: #e0e7ff;
            color: #4338ca;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
        .chapter-list {
            margin-top: 8px;
            list-style-type: none;
            padding-left: 12px;
            border-left: 2px solid #a8c0ff;
        }
        .tooltip {
            position: absolute;
            z-index: 10;
            padding: 8px;
            background-color: rgba(0, 0, 0, 0.85);
            color: white;
            border-radius: 6px;
            font-size: 0.875rem;
            max-width: 200px;
            word-wrap: break-word;
            display: none;
            pointer-events: none;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            margin-bottom: 10px;
        }
        .tooltip::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: rgba(0, 0, 0, 0.85) transparent transparent transparent;
        }
    </style>
</head>
<body class="flex items-center justify-center p-4 md:p-8">
    <div class="container relative flex flex-col items-center p-4 md:p-8">
        <div class="card w-full max-w-4xl mx-auto rounded-3xl shadow-2xl p-6 md:p-10 text-gray-800">
            <h1 class="text-4xl md:text-5xl font-bold text-center mb-2 text-purple-800">Study Planner</h1>

            <!-- Tabs Navigation & Main Content -->
            <div id="main-content" class="block">
                <div class="flex justify-center mb-6 overflow-x-auto">
                    <button data-tab="dashboard" class="tab-button active flex-1 md:flex-none py-3 px-6 rounded-t-xl hover:bg-white transition-colors">Tasks</button>
                    <button data-tab="timetable" class="tab-button flex-1 md:flex-none py-3 px-6 rounded-t-xl hover:bg-white transition-colors">Timetable</button>
                    <button data-tab="pomodoro" class="tab-button flex-1 md:flex-none py-3 px-6 rounded-t-xl hover:bg-white transition-colors">Pomodoro</button>
                    <button data-tab="subjects" class="tab-button flex-1 md:flex-none py-3 px-6 rounded-t-xl hover:bg-white transition-colors">Subjects</button>
                    <button data-tab="journal" class="tab-button flex-1 md:flex-none py-3 px-6 rounded-t-xl hover:bg-white transition-colors">Journal</button>
                </div>

                <div id="dashboard" class="tab-content active">
                    <h2 class="text-2xl font-semibold mb-4 text-purple-700">My Tasks</h2>
                    <form id="add-task-form" class="flex flex-col md:flex-row gap-4 mb-8">
                        <input type="text" id="task-input" placeholder="What do you need to study?" class="flex-grow p-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all">
                        <input type="date" id="date-input" class="p-3 rounded-xl border border-gray-300 text-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all">
                        <select id="subject-select" class="p-3 rounded-xl border border-gray-300 text-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all">
                            <option value="">Select Subject</option>
                        </select>
                        <button type="submit" class="bg-purple-600 text-white p-3 rounded-xl font-medium hover:bg-purple-700 transition-colors shadow-lg">Add Task</button>
                    </form>
                    <ul id="task-list" class="flex flex-col gap-3"></ul>
                </div>

                <div id="timetable" class="tab-content">
                    <h2 class="text-2xl font-semibold mb-4 text-purple-700">Timetable</h2>
                    <div class="flex justify-between items-center mb-4">
                        <button id="prev-month-btn" class="bg-purple-500 text-white p-2 rounded-full hover:bg-purple-600 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
                        </button>
                        <span id="current-month-year" class="text-xl font-semibold"></span>
                        <button id="next-month-btn" class="bg-purple-500 text-white p-2 rounded-full hover:bg-purple-600 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10l-3.293-3.293a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" /></svg>
                        </button>
                    </div>
                    <div id="calendar-body" class="calendar-grid"></div>
                </div>

                <div id="pomodoro" class="tab-content">
                    <h2 class="text-2xl font-semibold mb-4 text-purple-700">Pomodoro Timer</h2>
                    <div class="flex flex-col items-center justify-center p-6 bg-purple-50 rounded-xl shadow-inner mb-6">
                        <div id="timer-display" class="text-6xl md:text-8xl font-bold text-purple-900 mb-4">25:00</div>
                        <div class="text-md text-gray-600 mb-4" id="pomodoro-status">Ready to study!</div>
                        <div class="flex gap-4">
                            <button id="start-btn" class="bg-green-500 text-white py-3 px-8 rounded-full font-bold shadow-lg hover:bg-green-600 transition-colors">Start</button>
                            <button id="pause-btn" class="bg-yellow-500 text-white py-3 px-8 rounded-full font-bold shadow-lg hover:bg-yellow-600 transition-colors">Pause</button>
                            <button id="reset-btn" class="bg-red-500 text-white py-3 px-8 rounded-full font-bold shadow-lg hover:bg-red-600 transition-colors">Reset</button>
                        </div>
                    </div>
                    <h3 class="text-xl font-semibold mb-2 text-purple-700">Link to a Task</h3>
                    <div class="flex gap-4">
                        <select id="pomodoro-task-select" class="flex-grow p-3 rounded-xl border border-gray-300 text-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500">
                            <option value="">Select a Task</option>
                        </select>
                    </div>
                </div>

                <div id="subjects" class="tab-content">
                    <h2 class="text-2xl font-semibold mb-4 text-purple-700">Manage Subjects & Chapters</h2>
                    <form id="add-subject-form" class="flex flex-col md:flex-row gap-4 mb-8">
                        <input type="text" id="subject-input" placeholder="e.g., Physics, History" class="flex-grow p-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all">
                        <button type="submit" class="bg-purple-600 text-white p-3 rounded-xl font-medium hover:bg-purple-700 transition-colors shadow-lg">Add Subject</button>
                    </form>
                    <ul id="subject-list" class="flex flex-col gap-3"></ul>
                </div>

                <div id="journal" class="tab-content">
                    <h2 class="text-2xl font-semibold mb-4 text-purple-700">Daily Journal & Routine</h2>
                    <form id="journal-form" class="flex flex-col gap-4">
                        <textarea id="journal-text" placeholder="Write about what you learned today, your daily routine, or any thoughts..." rows="10" class="p-4 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"></textarea>
                        <button type="submit" class="bg-purple-600 text-white p-3 rounded-xl font-medium hover:bg-purple-700 transition-colors shadow-lg">Save Entry</button>
                    </form>
                </div>
            </div>
        </div>
        
        <!-- Custom Modal for Alerts -->
        <div id="custom-modal" class="fixed inset-0 bg-gray-900 bg-opacity-70 flex items-center justify-center p-4 hidden z-20">
            <div class="bg-white rounded-xl shadow-2xl p-6 max-w-sm w-full text-center">
                <p id="modal-message" class="text-lg font-semibold mb-4 text-gray-800"></p>
                <button id="modal-close" class="bg-purple-600 text-white py-2 px-6 rounded-lg hover:bg-purple-700 transition-colors">OK</button>
            </div>
        </div>
        
        <!-- Tooltip for Calendar -->
        <div id="calendar-tooltip" class="tooltip"></div>

        <script>
            // --- Utility functions to update the UI ---
            function showModal(message) {
                const modal = document.getElementById('custom-modal');
                const modalMessage = document.getElementById('modal-message');
                modalMessage.textContent = message;
                modal.classList.remove('hidden');
            }
            
            document.getElementById('modal-close').addEventListener('click', () => {
                document.getElementById('custom-modal').classList.add('hidden');
            });

            // --- Main App Logic ---
            async function fetchData() {
                const response = await fetch('/get_data');
                const data = await response.json();
                renderTasks(data.tasks, data.subjects);
                renderSubjects(data.subjects);
                renderCalendar(data.tasks);
                showDueTaskAlerts(data.tasks);
            }
            
            async function renderTasks(tasks, subjects) {
                const taskList = document.getElementById('task-list');
                const pomodoroSelect = document.getElementById('pomodoro-task-select');
                taskList.innerHTML = '';
                pomodoroSelect.innerHTML = '<option value="">Select a Task</option>';
                
                if (tasks.length === 0) {
                    taskList.innerHTML = '<li class="text-center p-4 text-gray-500">No tasks yet. Add one above!</li>';
                }
                
                tasks.forEach(task => {
                    const subject = subjects.find(s => s.id === task.subjectId);
                    const subjectName = subject ? subject.name : 'N/A';
                    const listItem = document.createElement('li');
                    listItem.className = `task-item flex items-center justify-between bg-white p-4 rounded-xl shadow-md transition-all duration-300 ${task.completed ? 'task-completed' : ''}`;
                    listItem.innerHTML = `
                        <div class="flex-grow">
                            <p class="text-lg font-semibold">${task.name}</p>
                            <p class="text-sm text-gray-500">Due: ${task.date}</p>
                            <p class="text-xs text-purple-500">Subject: ${subjectName}</p>
                            <p class="text-xs text-gray-400">Pomodoros: ${task.pomodoroSessions || 0}</p>
                        </div>
                        <div class="flex space-x-2 ml-4">
                            <button class="complete-btn bg-green-500 text-white p-2 rounded-full hover:bg-green-600 transition-colors" data-id="${task.id}">
                               <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
                            </button>
                            <button class="delete-btn bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition-colors" data-id="${task.id}">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-1 1v1H5a1 1 0 000 2h1v9a2 2 0 002 2h4a2 2 0 002-2V6h1a1 1 0 100-2h-3V3a1 1 0 00-1-1H9zm1 2v10a1 1 0 002 0V4h-2z" clip-rule="evenodd" /></svg>
                            </button>
                        </div>
                    `;
                    taskList.appendChild(listItem);
                    
                    const pomodoroOption = document.createElement('option');
                    pomodoroOption.value = task.id;
                    pomodoroOption.textContent = task.name;
                    pomodoroSelect.appendChild(pomodoroOption);
                });
                
                document.querySelectorAll('.complete-btn').forEach(btn => btn.addEventListener('click', async (e) => {
                    await fetch('/update_task', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ 'id': e.currentTarget.dataset.id, 'completed': true })
                    });
                    fetchData();
                }));
                
                document.querySelectorAll('.delete-btn').forEach(btn => btn.addEventListener('click', async (e) => {
                    await fetch('/delete_task', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ 'id': e.currentTarget.dataset.id })
                    });
                    fetchData();
                }));
            }
            
            async function renderSubjects(subjects) {
                const subjectList = document.getElementById('subject-list');
                const subjectSelect = document.getElementById('subject-select');
                subjectList.innerHTML = '';
                subjectSelect.innerHTML = '<option value="">Select Subject</option>';
                
                if (subjects.length === 0) {
                    subjectList.innerHTML = '<li class="text-center p-4 text-gray-500">No subjects yet. Add one above!</li>';
                }
                
                subjects.forEach(subject => {
                    const listItem = document.createElement('li');
                    listItem.className = 'bg-white p-4 rounded-xl shadow-md mb-2';
                    listItem.innerHTML = `
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-lg font-semibold">${subject.name}</span>
                            <div class="flex space-x-2">
                                <button class="add-chapter-btn bg-blue-500 text-white p-2 rounded-full hover:bg-blue-600 transition-colors" data-id="${subject.id}">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" /></svg>
                                </button>
                                <button class="delete-subject-btn bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition-colors" data-id="${subject.id}">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-1 1v1H5a1 1 0 000 2h1v9a2 2 0 002 2h4a2 2 0 002-2V6h1a1 1 0 100-2h-3V3a1 1 0 00-1-1H9zm1 2v10a1 1 0 002 0V4h-2z" clip-rule="evenodd" /></svg>
                            </button>
                        </div>
                    </div>
                    <ul class="chapter-list" data-subject-id="${subject.id}"></ul>
                    `;
                    subjectList.appendChild(listItem);
                    
                    const chapterList = listItem.querySelector('.chapter-list');
                    subject.chapters.forEach(chapter => {
                        const chapterItem = document.createElement('li');
                        chapterItem.className = 'flex items-center justify-between py-1 text-sm text-gray-600';
                        chapterItem.innerHTML = `
                            <span>${chapter.name}</span>
                            <button class="delete-chapter-btn text-red-400 hover:text-red-600" data-chapter-id="${chapter.id}" data-subject-id="${subject.id}">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-1 1v1H5a1 1 0 000 2h1v9a2 2 0 002 2h4a2 2 0 002-2V6h1a1 1 0 100-2h-3V3a1 1 0 00-1-1H9zm1 2v10a1 1 0 002 0V4h-2z" clip-rule="evenodd" /></svg>
                            </button>
                        `;
                        chapterList.appendChild(chapterItem);
                    });

                    const subjectOption = document.createElement('option');
                    subjectOption.value = subject.id;
                    subjectOption.textContent = subject.name;
                    subjectSelect.appendChild(subjectOption);
                });
                
                document.querySelectorAll('.delete-subject-btn').forEach(btn => btn.addEventListener('click', async (e) => {
                    await fetch('/delete_subject', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ 'id': e.currentTarget.dataset.id })
                    });
                    fetchData();
                }));

                document.querySelectorAll('.add-chapter-btn').forEach(btn => btn.addEventListener('click', async (e) => {
                    const chapterName = prompt("Enter the chapter name:");
                    if (chapterName) {
                        const response = await fetch('/add_chapter', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ 'subjectId': e.currentTarget.dataset.id, 'chapterName': chapterName })
                        });
                        if (response.ok) {
                            fetchData();
                        } else {
                            showModal('Failed to add chapter.');
                        }
                    }
                }));
                
                document.querySelectorAll('.delete-chapter-btn').forEach(btn => btn.addEventListener('click', async (e) => {
                    await fetch('/delete_chapter', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ 'subjectId': e.currentTarget.dataset.subjectId, 'chapterId': e.currentTarget.dataset.chapterId })
                    });
                    fetchData();
                }));
            }

            document.getElementById('add-task-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const taskName = document.getElementById('task-input').value.trim();
                const dueDate = document.getElementById('date-input').value;
                const subjectId = document.getElementById('subject-select').value;
                if (!taskName) { showModal('Please enter a task name.'); return; }
                
                const response = await fetch('/add_task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ 'name': taskName, 'date': dueDate, 'subjectId': subjectId })
                });
                
                if (response.ok) {
                    document.getElementById('task-input').value = '';
                    document.getElementById('date-input').value = '';
                    document.getElementById('subject-select').value = '';
                    fetchData();
                } else {
                    showModal('Failed to add task.');
                }
            });

            document.getElementById('add-subject-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const subjectName = document.getElementById('subject-input').value.trim();
                if (!subjectName) { showModal('Please enter a subject name.'); return; }
                
                const response = await fetch('/add_subject', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ 'name': subjectName })
                });

                if (response.ok) {
                    document.getElementById('subject-input').value = '';
                    fetchData();
                } else {
                    showModal('Failed to add subject.');
                }
            });

            // --- Calendar ---
            let currentDate = new Date();
            const calendarTooltip = document.getElementById('calendar-tooltip');
            
            function renderCalendar() {
                const calendarBody = document.getElementById('calendar-body');
                const currentMonthYear = document.getElementById('current-month-year');
                calendarBody.innerHTML = '';
                
                const startOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
                const endOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
                const startDate = new Date(startOfMonth);
                startDate.setDate(startOfMonth.getDate() - startOfMonth.getDay());
                
                currentMonthYear.textContent = currentDate.toLocaleString('default', { month: 'long', year: 'numeric' });

                const today = new Date();
                
                fetch('/get_data').then(res => res.json()).then(data => {
                    const taskMap = data.tasks.reduce((acc, task) => {
                        const date = task.date;
                        if (!acc[date]) acc[date] = [];
                        acc[date].push(task);
                        return acc;
                    }, {});

                    let tempDate = new Date(startDate);
                    while (tempDate <= endOfMonth || tempDate.getDay() !== 0) {
                        const dayDiv = document.createElement('div');
                        dayDiv.className = 'calendar-day relative p-2 rounded-xl transition-colors duration-200';
                        if (tempDate.getMonth() === currentDate.getMonth()) {
                            dayDiv.classList.add('current-month', 'shadow');
                        } else {
                            dayDiv.classList.add('text-gray-400');
                        }
                        if (tempDate.getDate() === today.getDate() && tempDate.getMonth() === today.getMonth() && tempDate.getFullYear() === today.getFullYear()) {
                            dayDiv.classList.add('bg-purple-100', 'border-2', 'border-purple-500');
                        }
                        const dayNumber = document.createElement('div');
                        dayNumber.textContent = tempDate.getDate();
                        dayNumber.className = 'font-semibold';
                        dayDiv.appendChild(dayNumber);
                        const dateKey = tempDate.toISOString().split('T')[0];
                        const dayTasks = taskMap[dateKey] || [];
                        if (dayTasks.length > 0) {
                            dayDiv.dataset.tasks = JSON.stringify(dayTasks.map(t => t.name));
                            const taskListDiv = document.createElement('ul');
                            taskListDiv.className = 'tasks';
                            dayTasks.forEach(task => {
                                const taskItem = document.createElement('li');
                                taskItem.textContent = task.name;
                                taskItem.className = `task-entry ${task.completed ? 'task-completed' : ''}`;
                                taskListDiv.appendChild(taskItem);
                            });
                            dayDiv.appendChild(taskListDiv);
                        }
                        calendarBody.appendChild(dayDiv);
                        tempDate.setDate(tempDate.getDate() + 1);
                    }

                    // Add hover events for tooltips
                    document.querySelectorAll('.calendar-day').forEach(day => {
                        day.addEventListener('mouseenter', (e) => {
                            const tasks = JSON.parse(e.currentTarget.dataset.tasks || '[]');
                            if (tasks.length > 0) {
                                calendarTooltip.innerHTML = tasks.join('<br>');
                                calendarTooltip.style.display = 'block';
                            }
                        });
                        day.addEventListener('mousemove', (e) => {
                            calendarTooltip.style.left = `${e.clientX}px`;
                            calendarTooltip.style.top = `${e.clientY}px`;
                        });
                        day.addEventListener('mouseleave', () => {
                            calendarTooltip.style.display = 'none';
                        });
                    });
                });
            }

            document.getElementById('prev-month-btn').addEventListener('click', () => {
                currentDate.setMonth(currentDate.getMonth() - 1);
                renderCalendar();
            });

            document.getElementById('next-month-btn').addEventListener('click', () => {
                currentDate.setMonth(currentDate.getMonth() + 1);
                renderCalendar();
            });

            // --- Pomodoro Timer ---
            let pomodoroTime = 25 * 60;
            let timerInterval;
            let isTimerRunning = false;
            let activeTaskId = null;
            
            function formatTime(seconds) {
                const minutes = Math.floor(seconds / 60);
                const remainingSeconds = seconds % 60;
                return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
            }

            document.getElementById('timer-display').textContent = formatTime(pomodoroTime);

            document.getElementById('start-btn').addEventListener('click', async () => {
                if (isTimerRunning) return;
                activeTaskId = document.getElementById('pomodoro-task-select').value;
                if (!activeTaskId) { showModal("Please select a task."); return; }
                
                isTimerRunning = true;
                document.getElementById('pomodoro-status').textContent = `Focusing on: ${document.getElementById('pomodoro-task-select').options[document.getElementById('pomodoro-task-select').selectedIndex].text}`;
                timerInterval = setInterval(() => {
                    if (pomodoroTime > 0) {
                        pomodoroTime--;
                        document.getElementById('timer-display').textContent = formatTime(pomodoroTime);
                    } else {
                        clearInterval(timerInterval);
                        isTimerRunning = false;
                        showModal("Session Complete!");
                        document.getElementById('pomodoro-status').textContent = "Session Complete!";
                        fetch('/increment_pomodoro', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ 'id': activeTaskId })
                        });
                        setTimeout(() => {
                            pomodoroTime = 25 * 60;
                            document.getElementById('timer-display').textContent = formatTime(pomodoroTime);
                        }, 1000);
                    }
                }, 1000);
            });

            document.getElementById('pause-btn').addEventListener('click', () => {
                clearInterval(timerInterval);
                isTimerRunning = false;
                document.getElementById('pomodoro-status').textContent = "Timer Paused";
            });

            document.getElementById('reset-btn').addEventListener('click', () => {
                clearInterval(timerInterval);
                isTimerRunning = false;
                pomodoroTime = 25 * 60;
                document.getElementById('timer-display').textContent = formatTime(pomodoroTime);
                document.getElementById('pomodoro-status').textContent = "Ready to study!";
                activeTaskId = null;
            });

            // --- Journal ---
            async function loadJournalEntry() {
                const today = new Date().toISOString().split('T')[0];
                const response = await fetch(`/journal/${today}`);
                const data = await response.json();
                document.getElementById('journal-text').value = data.entry || '';
            }

            document.getElementById('journal-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const entry = document.getElementById('journal-text').value;
                if (!entry.trim()) { showModal('Journal entry cannot be empty.'); return; }
                
                const response = await fetch('/save_journal', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ 'entry': entry })
                });

                if (response.ok) {
                    showModal('Journal entry saved!');
                } else {
                    showModal('Failed to save journal entry.');
                }
            });
            
            // Initial data load on page load and tab switching
            window.onload = () => {
                fetchData();
                document.querySelectorAll('.tab-button').forEach(button => {
                    button.addEventListener('click', () => {
                        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                        
                        button.classList.add('active');
                        document.getElementById(button.dataset.tab).classList.add('active');
                        
                        // Add specific logic for each tab here
                        if (button.dataset.tab === 'timetable') {
                            renderCalendar();
                        } else if (button.dataset.tab === 'journal') {
                            loadJournalEntry();
                        } else if (button.dataset.tab === 'dashboard') {
                            fetchData();
                        }
                    });
                });
            };

            async function showDueTaskAlerts(tasks) {
                const today = new Date();
                const dueTasks = tasks.filter(task => {
                    if (task.completed) return false;
                    const dueDate = new Date(task.date);
                    const timeDiff = dueDate.getTime() - today.getTime();
                    const dayDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
                    return dayDiff >= 0 && dayDiff <= 2;
                });
                
                if (dueTasks.length > 0) {
                    const taskList = dueTasks.map(t => `- ${t.name} (due on ${t.date})`).join('\\n');
                    showModal(`You have tasks due soon!\\n\\n${taskList}`);
                }
            }
        </script>
    </body>
</html>
"""
    return render_template_string(html_content)

# --- API Endpoints ---
@app.route('/get_data')
def get_data():
    """Endpoint to get all planner data."""
    data = load_data()
    return jsonify(data)

@app.route('/add_task', methods=['POST'])
def add_task():
    """Endpoint to add a new task."""
    data = load_data()
    new_task = request.json
    new_task['id'] = str(uuid.uuid4())
    new_task['completed'] = False
    new_task['pomodoroSessions'] = 0
    data['tasks'].append(new_task)
    save_data(data)
    return jsonify({'success': True})

@app.route('/update_task', methods=['POST'])
def update_task():
    """Endpoint to update a task."""
    data = load_data()
    update_data = request.json
    for task in data['tasks']:
        if task['id'] == update_data['id']:
            task.update(update_data)
            # Add to journal if completed
            if update_data.get('completed'):
                today = datetime.now().strftime('%Y-%m-%d')
                if today not in data['journal']:
                    data['journal'][today] = "Completed tasks:\n"
                
                # Check if the task is already logged in today's journal
                task_entry = f"- {task['name']}\n"
                if task_entry not in data['journal'][today]:
                    data['journal'][today] += task_entry
            break
    save_data(data)
    return jsonify({'success': True})

@app.route('/delete_task', methods=['POST'])
def delete_task():
    """Endpoint to delete a task."""
    data = load_data()
    task_id = request.json['id']
    data['tasks'] = [t for t in data['tasks'] if t['id'] != task_id]
    save_data(data)
    return jsonify({'success': True})

@app.route('/add_subject', methods=['POST'])
def add_subject():
    """Endpoint to add a new subject."""
    data = load_data()
    new_subject = request.json
    new_subject['id'] = str(uuid.uuid4())
    new_subject['chapters'] = []
    data['subjects'].append(new_subject)
    save_data(data)
    return jsonify({'success': True})

@app.route('/delete_subject', methods=['POST'])
def delete_subject():
    """Endpoint to delete a subject."""
    data = load_data()
    subject_id = request.json['id']
    data['subjects'] = [s for s in data['subjects'] if s['id'] != subject_id]
    save_data(data)
    return jsonify({'success': True})

@app.route('/add_chapter', methods=['POST'])
def add_chapter():
    """Endpoint to add a new chapter to a subject."""
    data = load_data()
    request_data = request.json
    subject_id = request_data.get('subjectId')
    chapter_name = request_data.get('chapterName')

    for subject in data['subjects']:
        if subject['id'] == subject_id:
            subject['chapters'].append({
                'id': str(uuid.uuid4()),
                'name': chapter_name
            })
            break
    
    save_data(data)
    return jsonify({'success': True})

@app.route('/delete_chapter', methods=['POST'])
def delete_chapter():
    """Endpoint to delete a chapter from a subject."""
    data = load_data()
    request_data = request.json
    subject_id = request_data.get('subjectId')
    chapter_id = request_data.get('chapterId')

    for subject in data['subjects']:
        if subject['id'] == subject_id:
            subject['chapters'] = [c for c in subject['chapters'] if c['id'] != chapter_id]
            break
    
    save_data(data)
    return jsonify({'success': True})

@app.route('/increment_pomodoro', methods=['POST'])
def increment_pomodoro():
    """Endpoint to increment pomodoro count for a task."""
    data = load_data()
    task_id = request.json['id']
    for task in data['tasks']:
        if task['id'] == task_id:
            task['pomodoroSessions'] = task.get('pomodoroSessions', 0) + 1
            break
    save_data(data)
    return jsonify({'success': True})

@app.route('/save_journal', methods=['POST'])
def save_journal():
    """Endpoint to save a journal entry. Can only be done for the current day."""
    data = load_data()
    entry = request.json['entry']
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Prepend existing completed tasks
    completed_tasks_text = ""
    if today in data['journal'] and "Completed tasks:" in data['journal'][today]:
        completed_tasks_text = data['journal'][today]
        data['journal'][today] = entry + "\n\n" + completed_tasks_text
    else:
        data['journal'][today] = entry

    save_data(data)
    return jsonify({'success': True})

@app.route('/journal/<date_str>')
def get_journal_entry(date_str):
    """Endpoint to get a specific journal entry."""
    data = load_data()
    return jsonify({'entry': data['journal'].get(date_str, '')})

if __name__ == '__main__':
    app.run(debug=True)
