
const API_BASE = "/api/v1"; // Uses current origin (localhost or IP) automatically

// Get Session ID from URL
const urlParams = new URLSearchParams(window.location.search);
const sessionId = urlParams.get('session_id');

const fileInput = document.getElementById('file-input');
const dropZone = document.getElementById('drop-zone');
const statusDiv = document.getElementById('status');
const progressContainer = document.getElementById('progress-container');
const progressBar = document.getElementById('progress-bar');

if (!sessionId) {
    statusDiv.style.color = "red";
    statusDiv.innerText = "Invalid Session. Scan QR again.";
    dropZone.style.pointerEvents = "none";
}

dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
        alert("Only PDF files are allowed.");
        return;
    }

    uploadFile(file);
});

async function uploadFile(file) {
    statusDiv.innerText = "Preparing upload...";
    progressContainer.style.display = "block";

    try {
        // 1. Get Presigned URL
        const res = await fetch(`${API_BASE}/session/${sessionId}/upload-url?filename=${encodeURIComponent(file.name)}`);
        if (!res.ok) throw new Error("Failed to get upload URL");
        const data = await res.json();
        const uploadUrl = data.url;
        const fileKey = data.key;

        // 2. Upload to S3
        statusDiv.innerText = "Uploading...";
        const uploadRes = await fetch(uploadUrl, {
            method: 'PUT',
            body: file,
            headers: { 'Content-Type': 'application/pdf' }
        });

        if (!uploadRes.ok) {
            const errText = await uploadRes.text();
            throw new Error(`Upload failed ${uploadRes.status}: ${errText}`);
        }

        progressBar.style.width = "100%";

        // 3. Notify Backend
        statusDiv.innerText = "Processing...";
        const finalRes = await fetch(`${API_BASE}/session/${sessionId}/uploaded?key=${encodeURIComponent(fileKey)}`, {
            method: 'POST'
        });

        if (finalRes.ok) {
            // Hide Progress and Status Text
            statusDiv.style.display = 'none';
            progressContainer.style.display = 'none';
            dropZone.style.display = "none";

            // Show Success Card
            const successCard = document.getElementById('success-card');
            document.getElementById('uploaded-filename').innerText = file.name;
            document.getElementById('uploaded-size').innerText = formatBytes(file.size);
            successCard.style.display = 'block';

        } else {
            const errText = await finalRes.text();
            throw new Error(`Finalization failed ${finalRes.status}: ${errText}`);
        }
    } catch (e) {
        statusDiv.style.color = "red";
        statusDiv.innerText = "Error: " + e.message;
        progressBar.style.backgroundColor = "red";
    }
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}


