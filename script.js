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

// Function to process files (Now sends files to the server)
async function processFiles() {
    const files = document.getElementById('fileInput').files;
    const targetLanguage = document.getElementById('targetLanguage').value;

    if (files.length === 0) {
        alert('Please select files to translate.');
        return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    formData.append('targetLanguage', targetLanguage); // Send target language

    try {
        const response = await fetch('/translate_files', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Display Translations (Adapt this part based on how you want to show the results)
        let output = '';
        for (const filename in data) {
            output += `<p><b>${filename}:</b> ${data[filename]}</p>`;
        }
        document.getElementById('outputText').innerHTML = output;

    } catch (error) {
        console.error('Error processing files:', error);
        alert('Error processing files. See console for details.');
    }
}

// Function to translate text (Now sends text to the server)
async function translateText() {
    const inputText = document.getElementById('inputText').value;
    const sourceLanguage = document.getElementById('sourceLanguage').value;
    const targetLanguage = document.getElementById('targetLanguage').value;

    if (!inputText) {
        alert('Please enter text to translate.');
        return;
    }

    const formData = new FormData();
    formData.append('text', inputText);
    formData.append('sourceLanguage', sourceLanguage);
    formData.append('targetLanguage', targetLanguage);

    try {
        const response = await fetch('/translate_text', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        document.getElementById('outputText').textContent = data.translated_text;

    } catch (error) {
        console.error('Error translating text:', error);
        alert('Error translating text. See console for details.');
    }
}
