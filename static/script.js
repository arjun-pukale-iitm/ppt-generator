// your code goes here
document.getElementById('pptxForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const statusDiv = document.getElementById('status');
    statusDiv.textContent = "Uploading and processing… Please wait.";

    const formData = new FormData();
    formData.append('text', document.getElementById('text').value);
    formData.append('guidance', document.getElementById('guidance').value);
    formData.append('provider', document.getElementById('provider').value);
    formData.append('api_key', document.getElementById('api_key').value);
    formData.append('template', document.getElementById('template').files[0]);

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const err = await response.text();
            statusDiv.textContent = `Error: ${err}`;
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = 'generated.pptx';
        document.body.appendChild(a);
        a.click();
        a.remove();

        statusDiv.textContent = "Presentation generated! Download should start automatically.";
    } catch (err) {
        statusDiv.textContent = `Error: ${err.message}`;
    }
});
