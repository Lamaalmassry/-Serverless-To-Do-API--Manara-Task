async function loadTasks() {
    try {
        const response = await fetch(`${apiBase}/tasks`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const tasks = await response.json();
        const list = document.getElementById("task-list");
        list.innerHTML = "";

        tasks.forEach(task => {
            const li = document.createElement("li");
            li.className = "task-card";

            li.innerHTML = `
                <div class="task-title">${task.title || '(No Title)'}</div>
                <div class="task-meta">${task.description || '(No Description)'}</div>
                <div class="task-meta">
                    <strong>Status:</strong> ${task.status || 'Pending'} |
                    <strong>Priority:</strong> ${task.priority || 'medium'} |
                    <strong>Due:</strong> ${task.due_date || 'N/A'}
                </div>
                <div class="task-meta">
                    <strong>Created at:</strong> ${new Date(task.createdAt).toLocaleString()}
                </div>
                <div class="task-meta">
                    <strong>ID:</strong> ${task.taskId}
                </div>
                <div class="task-buttons">
                    <button class="update" onclick="updateTask('${task.taskId}')">Update</button>
                    <button class="delete" onclick="deleteTask('${task.taskId}')">Delete</button>
                </div>
            `;

            list.appendChild(li);
        });
    } catch (error) {
        console.error("Error loading tasks:", error);
        alert("Failed to load tasks. Check console for details.");
    }
}
const apiBase = "https://eoss66b47k.execute-api.us-east-1.amazonaws.com"; // Update if needed

async function addTask() {
    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();
    const status = document.getElementById("status").value;
    const priority = document.getElementById("priority").value;
    const due_date = document.getElementById("due_date").value;

    if (!title) {
        alert("Title is required.");
        return;
    }

    const task = { title, description, status, priority, due_date };

    try {
        const response = await fetch(`${apiBase}/tasks`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(task)
        });

        if (!response.ok) throw new Error(`Failed to add task: ${response.statusText}`);

        // Clear form
        document.getElementById("title").value = "";
        document.getElementById("description").value = "";
        document.getElementById("status").value = "Pending";
        document.getElementById("priority").value = "medium";
        document.getElementById("due_date").value = "";

        loadTasks(); // Refresh list
    } catch (error) {
        console.error("Error adding task:", error);
        alert("Failed to add task. Check console for details.");
    }
}

async function updateTask(taskId) {
    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();
    const status = document.getElementById("status").value;
    const priority = document.getElementById("priority").value;
    const due_date = document.getElementById("due_date").value;

    if (!title) {
        alert("Title is required to update.");
        return;
    }

    const updatedTask = { title, description, status, priority, due_date };

    try {
        const response = await fetch(`${apiBase}/tasks/${taskId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updatedTask)
        });

        if (!response.ok) throw new Error(`Update failed: ${response.statusText}`);
        loadTasks();
    } catch (error) {
        console.error("Error updating task:", error);
        alert("Failed to update task.");
    }
}
async function deleteTask(taskId) {
    const confirmDelete = confirm("Are you sure you want to delete this task?");
    if (!confirmDelete) return;

    try {
        const response = await fetch(`${apiBase}/tasks/${taskId}`, {
            method: "DELETE"
        });

        if (!response.ok) throw new Error(`Delete failed: ${response.statusText}`);
        loadTasks();
    } catch (error) {
        console.error("Error deleting task:", error);
        alert("Failed to delete task.");
    }
}
