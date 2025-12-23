
const API_BASE = "/api/v1"; // Uses current origin automatically
const POLLING_INTERVAL = 2000;
const MACHINE_ID = 1; // HARDCODED FOR DEMO, should be configured or fetched

let currentSessionId = null;
let pollInterval = null;



const app = document.getElementById('app');

// Auth Check
if (!localStorage.getItem('admin_token')) {
    window.location.href = '/admin';
}

// Auto-start session on load
window.addEventListener('DOMContentLoaded', startSession);

// --- Secure Admin Logic ---
let pendingAction = null; // 'logout' or 'price'
let savedAdminUsername = localStorage.getItem('admin_username') || 'admin'; // Fallback if missing

function toggleKioskMenu() {
    const dropdown = document.getElementById("kiosk-dropdown");
    const button = document.querySelector(".admin-nav-btn");

    dropdown.classList.toggle("show");
    button.classList.toggle("rotated"); // Toggle rotation
}

// Close dropdown if clicked outside
window.onclick = function (event) {
    if (!event.target.matches('.admin-nav-btn')) {
        const button = document.querySelector(".admin-nav-btn");
        var dropdowns = document.getElementsByClassName("kiosk-dropdown-content");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
                if (button) button.classList.remove('rotated'); // Remove rotation
            }
        }
    }
    if (event.target == document.getElementById('security-modal')) {
        closeModal();
    }
}

function openAuthModal(action) {
    pendingAction = action;
    document.getElementById('security-modal').style.display = 'block';

    // Reset State
    document.getElementById('modal-auth-step').style.display = 'block';
    document.getElementById('modal-price-step').style.display = 'none';
    document.getElementById('modal-password').value = '';
    document.getElementById('modal-error').innerText = '';

    const title = action === 'logout' ? "Confirm Logout" : "Edit Price";
    document.getElementById('modal-title').innerText = title;
}

function closeModal() {
    document.getElementById('security-modal').style.display = 'none';
    pendingAction = null;
}

async function verifyAndProceed() {
    const password = document.getElementById('modal-password').value;
    const errorEl = document.getElementById('modal-error');

    if (!password) {
        errorEl.innerText = "Password required";
        return;
    }

    // Verify by hitting Login API
    const formData = new URLSearchParams();
    formData.append('username', savedAdminUsername);
    formData.append('password', password);

    try {
        const res = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (!res.ok) throw new Error("Incorrect Password");

        // Auth Success
        if (pendingAction === 'logout') {
            localStorage.removeItem('admin_token');
            localStorage.removeItem('admin_username');
            window.location.href = '/admin';
        } else if (pendingAction === 'price') {
            // Show Price UI
            showPriceUI();
        }

    } catch (e) {
        errorEl.innerText = e.message;
    }
}

async function showPriceUI() {
    document.getElementById('modal-auth-step').style.display = 'none';
    document.getElementById('modal-price-step').style.display = 'block';

    // Fetch current price (using the token we already have, or the new one if we updated logic, 
    // but the existing token is valid so we use that)
    const token = localStorage.getItem('admin_token'); // use stored token

    // We don't have a direct "GET Machine Price" except via session creation or admin endpoint
    // Let's use session init since we can't easily GET machine price without session or complex admin calls?
    // Wait, `/machine/{id}` is not exposed?
    // I can modify backend to expose GET /machine/{id} public content or simple auth
    // BUT for now in MVP, I'll rely on global `price_per_page` I likely stored or can get.
    // Actually, I can just fetch `/session` to see price? 
    // Or I'll just leave it blank and ask for NEW price.
    document.getElementById('current-price-display').innerText = "?";
}

async function confirmPriceUpdate() {
    const newPrice = document.getElementById('new-price-input').value;
    if (!newPrice) return;

    const token = localStorage.getItem('admin_token');

    try {
        const res = await fetch(`${API_BASE}/machine/${MACHINE_ID}/price`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ price_per_page: parseFloat(newPrice) })
        });

        if (res.ok) {
            alert("Price Updated!");
            closeModal();
            // Reload to reflect changes if needed
            location.reload();
        } else {
            alert("Failed to update");
        }
    } catch (e) {
        alert("Error: " + e.message);
    }
}

// --- End Secure Admin Logic ---

function updateStepper(step) {
    // Reset all
    document.querySelectorAll('.step').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.step-line').forEach(el => el.classList.remove('active'));

    // Activate specific steps
    if (step === 'scan') {
        document.getElementById('step-scan').classList.add('active');
    } else if (step === 'preview') {
        document.getElementById('step-scan').classList.add('active');
        document.querySelector('.stepper-container .step-line:nth-child(2)').classList.add('active'); // Line 1
        document.getElementById('step-preview').classList.add('active');
    } else if (step === 'payment') {
        document.getElementById('step-scan').classList.add('active');
        document.querySelector('.stepper-container .step-line:nth-child(2)').classList.add('active');
        document.getElementById('step-preview').classList.add('active');
        document.querySelector('.stepper-container .step-line:nth-child(4)').classList.add('active'); // Line 2
        document.getElementById('step-payment').classList.add('active');
    }
}

async function startSession() {
    try {
        const token = localStorage.getItem('admin_token');
        const res = await fetch(`${API_BASE}/session/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // Optional if backend checks it for session creation
            },
            body: JSON.stringify({ machine_id: MACHINE_ID })
        });
        const data = await res.json();
        currentSessionId = data.session_id;
        renderUploadScreen(data.upload_url);
        startPolling();
    } catch (e) {
        console.error(e);
        app.innerHTML = `<h1>Error connecting to server</h1><button class="btn" onclick="location.reload()">Retry</button>`;
    }
}

function startPolling() {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(checkStatus, POLLING_INTERVAL);
}

async function checkStatus() {
    if (!currentSessionId) return;
    try {
        const res = await fetch(`${API_BASE}/session/${currentSessionId}`);
        const session = await res.json();

        console.log("Status:", session.status);

        if (session.status === 'UPLOADED' && !document.getElementById('confirm-btn')) {
            renderPreviewScreen(session);
        } else if (session.status === 'CONFIRMED' && !document.getElementById('payment-qr')) {
            renderPaymentScreen(session); // Actually backend might update status to PAYMENT_PENDING? No, we handle that flow.
        } else if (session.status === 'PAID') {
            renderPrintingScreen();
        } else if (session.status === 'PRINTED') {
            renderSuccessScreen();
            clearInterval(pollInterval);
            setTimeout(() => location.reload(), 5000);
        }
    } catch (e) {
        console.error("Polling error", e);
    }
}

function renderUploadScreen(qrCode) {
    updateStepper('scan');
    // Construct the simulation URL
    const simUrl = `/mobile/upload.html?session_id=${currentSessionId}`;

    app.innerHTML = `
        <div class="upload-screen">
            <div class="upload-card glass-panel">
                <div class="payment-header">
                    <h1>Scan to Upload</h1>
                    <p>Use your mobile phone to scan and upload a PDF</p>
                </div>

                <div class="qr-wrapper">
                    <a href="${simUrl}" target="_blank" title="Click to Simulate Scan (Dev Mode)">
                        <div class="qr-frame">
                            <img src="${qrCode}" alt="Upload QR" />
                            <div class="scan-line"></div>
                        </div>
                    </a>
                </div>

                <div class="upload-status">
                    <div class="loader-spinner"></div>
                    <span>Waiting for scan...</span>
                </div>
                
                <p class="dev-note">
                    (Dev: Click QR to test on PC)
                </p>
            </div>
        </div>
    `;

}


function renderPreviewScreen(session) {
    updateStepper('preview');
    // Determine the File URL
    // session.file_name is likely "session_id/filename.pdf" (the key)
    // We can fetch it via /api/v1/storage/file/{key}
    const fileUrl = `${API_BASE}/storage/file/${session.file_name}`;

    app.innerHTML = `
        <div class="preview-screen">
            <div class="split-container">
                <!-- Left Side: PDF Preview -->
                <div class="preview-pane">
                    <h3>Document Preview</h3>
                    <div class="a4-preview-container">
                        <iframe src="${fileUrl}" title="PDF Preview"></iframe>
                    </div>
                </div>

                <!-- Right Side: Actions & Mini Details -->
                <div class="details-pane">
                    <div class="actions-wrapper">
                        <button id="confirm-btn" class="btn" onclick="confirmSession()">CONFIRM & PAY</button>
                        <div class="helper-text" style="text-align: center; margin-top: 15px;">Please review your document on the left before confirming.</div>
                    </div>

                    <div class="mini-details">
                        <div class="file-info">${session.file_name.split('/').pop()}</div>
                        <div class="stats-info">Pages: ${session.page_count} • ₹${session.price_per_page} / pg</div>
                        <div class="mini-price">Total: ₹${session.total_amount}</div>
                    </div>
                </div>
            </div>
        </div>
    `;

}

async function confirmSession() {
    await fetch(`${API_BASE}/session/${currentSessionId}/confirm`, { method: 'POST' });
    // After confirm, trigger payment generation
    const res = await fetch(`${API_BASE}/payment/${currentSessionId}/create`, { method: 'POST' });
    const data = await res.json();
    renderPaymentScreen({ total_amount: "CHECKING..." }, data);

    // In real flow, we wait for status change to PAID.
    // For demo, we can simulate payment success if we want, or just wait.
    // Let's add a hidden "Simulate Pay" button for testing 
    const debugBtn = document.createElement('button');
    debugBtn.innerText = "Simulate Payment";
    debugBtn.style = "position:absolute; bottom:10px; opacity:0.3;";
    debugBtn.onclick = async () => {
        await fetch(`${API_BASE}/payment/${currentSessionId}/mock-success`, { method: 'POST' });
    };
    app.appendChild(debugBtn);
    // Debug Shortcut: Check URL for ?debug=payment
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('debug') === 'payment') {
        renderPaymentScreen(
            { total_amount: 50.00 },
            { qr_code: "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi%3A%2F%2Fpay" } // Mock QR
        );
    }
}

// Make QR Clickable in renderPaymentScreen (Update)
function renderPaymentScreen(session, paymentData) {
    updateStepper('payment');
    app.innerHTML = `
        <div class="payment-screen">
            <div class="payment-card glass-panel">
                <div class="payment-header">
                    <h1>Scan & Pay</h1>
                    <p>Complete your payment to start printing</p>
                </div>

                <div class="qr-wrapper">
                    <a href="${paymentData.payment_url || '#'}" target="_blank">
                        <div class="qr-frame">
                            <img src="${paymentData.qr_code}" alt="Payment QR" />
                            <div class="scan-line"></div>
                        </div>
                    </a>
                    <div class="payment-amount">
                        <span class="currency">₹</span>
                        <span class="amount">${session.total_amount || '--'}</span>
                    </div>
                </div>

                <div class="payment-status">
                    <div class="loader-spinner"></div>
                    <span>Waiting for confirmation...</span>
                </div>
                
                <div class="supported-apps">
                    <span>Google Pay</span> • <span>PhonePe</span> • <span>Paytm</span>
                </div>
            </div>
        </div>
    `;

}


function renderPrintingScreen() {
    app.innerHTML = `
        <div class="status-badge">Step 4: Printing</div>
        <h1>Printing in Progress...</h1>
        <p>Please wait while your document is being printed.</p>
        <div style="font-size:5rem;">🖨️</div>
    `;
}

function renderSuccessScreen() {
    app.innerHTML = `
        <div class="status-badge">Done</div>
        <h1>Thank You!</h1>
        <p>Please collect your documents.</p>
        <div style="font-size:5rem;">✅</div>
    `;
}

// Init handled by auto-start
// app.innerHTML = `<h1>Welcome</h1><button class="btn" onclick="startSession()">Start Printing</button>`;
