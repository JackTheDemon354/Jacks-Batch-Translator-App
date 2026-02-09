// Function to handle file selection and display file names
document.getElementById('fileInput').addEventListener('change', function(event) {
    const fileListDiv = document.getElementById('fileList');
    fileListDiv.innerHTML = ''; // Clear previous file list
    const files = event.target.files;

    if (files.length > 50) {
        alert('You can only upload a maximum of 50 files.');
        this.value = ''; // Clear selected files
        return;
    }

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const fileElement = document.createElement('p');
        fileElement.textContent = file.name;
        fileListDiv.appendChild(fileElement);
    }
});

// Function to process files (Placeholder for actual translation logic)
function processFiles() {
    const files = document.getElementById('fileInput').files;
    if (files.length === 0) {
        alert('Please select files to translate.');
        return;
    }

    // Placeholder: Add actual image/PDF translation logic here
    alert(`Processing ${files.length} files for translation.`);
}

// Function to translate text (Placeholder for actual translation logic)
function translateText() {
    const inputText = document.getElementById('inputText').value;
    const sourceLanguage = document.getElementById('sourceLanguage').value;
    const targetLanguage = document.getElementById('targetLanguage').value;

    if (!inputText) {
        alert('Please enter text to translate.');
        return;
    }

    // Placeholder: Add actual text translation logic here using an API
    const translatedText = `Translated from ${sourceLanguage} to ${targetLanguage}: ${inputText}`;
    document.getElementById('outputText').textContent = translatedText;
}
