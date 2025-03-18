document.getElementById('processBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('pdfFile');
    const file = fileInput.files[0];
    if (!file) return alert('Please select a PDF file');

    const formData = new FormData();
    formData.append('file', file);

    const progress = document.getElementById('progress');
    progress.value = 10;

    const response = await fetch('/process_pdf', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    progress.value = 50;

    document.getElementById('textOutput').innerText = result.text || result.error;
    if (result.audio) {
        const audioPlayer = document.getElementById('audioPlayer');
        audioPlayer.src = result.audio;
        document.getElementById('playBtn').disabled = false;
        document.getElementById('stopBtn').disabled = false;
        progress.value = 100;
    }
});

document.getElementById('playBtn').addEventListener('click', () => {
    document.getElementById('audioPlayer').play();
});

document.getElementById('stopBtn').addEventListener('click', () => {
    document.getElementById('audioPlayer').pause();
});

// Fetch available voices (optional, if using ElevenLabs)
async function loadVoices() {
    const response = await fetch('/get_voices');
    const voices = await response.json();
    const voiceSelect = document.getElementById('voiceSelect');
    voices.forEach(voice => {
        const option = document.createElement('option');
        option.value = voice.id;
        option.text = voice.name;
        voiceSelect.appendChild(option);
    });
}
loadVoices();