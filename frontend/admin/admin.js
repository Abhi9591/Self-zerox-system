
const API_BASE = "http://localhost:8000/api/v1";

const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const authSection = document.getElementById('auth-section');
const lockSection = document.getElementById('lock-section');
const dashboardSection = document.getElementById('dashboard-section');
const authError = document.getElementById('auth-error');
const unlockError = document.getElementById('unlock-error');

let token = localStorage.getItem('admin_token');
let currentMachineId = null;
let savedUsername = localStorage.getItem('admin_username') || ''; // We need username for re-auth

// Init
if (token) {
    // SECURITY: Don't show dashboard directly. Show Lock Screen.
    showLockScreen();
} else {
    showLogin();
}

function showLockScreen() {
    authSection.style.display = 'none';
    dashboardSection.style.display = 'none';
    lockSection.style.display = 'block';
}

function showLogin() {
    authSection.style.display = 'block';
    lockSection.style.display = 'none';
    dashboardSection.style.display = 'none';

    loginForm.style.display = 'block';
    registerForm.style.display = 'none';
    document.getElementById('btn-login').classList.add('active');
    document.getElementById('btn-register').classList.remove('active');
    authError.innerText = '';
}

function showRegister() {
    loginForm.style.display = 'none';
    registerForm.style.display = 'block';
    document.getElementById('btn-login').classList.remove('active');
    document.getElementById('btn-register').classList.add('active');
    authError.innerText = '';
}

// Login Handler
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    await performLogin(username, password);
});

async function performLogin(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
        const res = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (!res.ok) throw new Error("Invalid Credentials");

        const data = await res.json();
        token = data.access_token;
        localStorage.setItem('admin_token', token);
        localStorage.setItem('admin_username', username); // Save for unlock flow

        // From Login -> Direct Dashboard is okay? 
        // Or Force Lock?
        // Let's go Direct since they just typed it.
        showDashboard();
    } catch (err) {
        authError.innerText = err.message;
        if (unlockError) unlockError.innerText = err.message;
    }
}


// Register Handler
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    const machineCode = document.getElementById('reg-machine').value;

    try {
        const regRes = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, machine_code: machineCode })
        });

        if (!regRes.ok) {
            const err = await regRes.json();
            throw new Error(err.detail || "Registration failed");
        }

        // Auto Login
        await performLogin(username, password);

        // Bind (idempotent, handled inside performLogin flow or manual?)
        // performLogin goes to dashboard. We need to Activate first.
        // Wait, binding is done via /machine/activate using the token we just got.

        // Since performLogin is async, we already have token here.
        await fetch(`${API_BASE}/machine/activate`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ machine_code: machineCode })
        });

    } catch (err) {
        authError.innerText = err.message;
    }
});

async function unlockDashboard() {
    const password = document.getElementById('unlock-password').value;
    if (!savedUsername) {
        unlockError.innerText = "Session expired. Please logout.";
        return;
    }

    // Verify by re-logging in
    try {
        await performLogin(savedUsername, password);
    } catch (e) {
        unlockError.innerText = "Incorrect Password";
    }
}


async function showDashboard() {
    authSection.style.display = 'none';
    lockSection.style.display = 'none';
    dashboardSection.style.display = 'block';

    try {
        currentMachineId = 1;
        document.getElementById('dash-machine-code').innerText = "Main Kiosk (ID: 1)";

        const res = await fetch(`${API_BASE}/session/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ machine_id: 1 })
        });
        const session = await res.json();
        document.getElementById('dash-price').value = session.price_per_page;

    } catch (e) {
        console.error(e);
    }
}

async function updatePrice() {
    const price = document.getElementById('dash-price').value;
    if (!currentMachineId) return;

    try {
        const res = await fetch(`${API_BASE}/machine/${currentMachineId}/price`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ price_per_page: parseFloat(price) })
        });

        if (res.ok) {
            document.getElementById('dash-msg').style.color = 'green';
            document.getElementById('dash-msg').innerText = 'Price updated!';
        } else {
            throw new Error("Failed to update");
        }
    } catch (e) {
        document.getElementById('dash-msg').style.color = 'red';
        document.getElementById('dash-msg').innerText = e.message;
    }
}

function toggleMenu() {
    document.getElementById("user-dropdown").classList.toggle("show");
}

window.onclick = function (event) {
    if (!event.target.matches('.settings-btn')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) openDropdown.classList.remove('show');
        }
    }
}

function launchDisplay() {
    window.location.href = '/kiosk';
}

function logout() {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_username');
    location.reload();
}
