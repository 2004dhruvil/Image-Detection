document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeBtn = document.getElementById('remove-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    const resultModal = document.getElementById('result-modal');
    const closeModal = document.querySelector('.close-modal');
    
    // Result elements
    const resultTitle = document.getElementById('result-title');
    const resultConfidence = document.getElementById('result-confidence');
    const resultIcon = document.getElementById('result-icon');
    const meterBar = document.getElementById('meter-bar');
    const resultTheory = document.getElementById('result-theory');

    // Drag and Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    dropZone.addEventListener('drop', handleDrop, false);
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFiles);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles({ target: { files: files } });
    }

    function handleFiles(e) {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onloadend = function() {
                imagePreview.src = reader.result;
                dropZone.style.display = 'none';
                previewContainer.style.display = 'block';
                analyzeBtn.disabled = false;
            }
        }
    }

    // Remove Image
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent triggering dropZone click if layered
        fileInput.value = '';
        dropZone.style.display = 'block';
        previewContainer.style.display = 'none';
        analyzeBtn.disabled = true;
    });

    // Analyze Image
    analyzeBtn.addEventListener('click', () => {
        if (!fileInput.files[0] && !dropZone.files) return;

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        // Show loading
        loadingOverlay.style.display = 'flex';
        analyzeBtn.disabled = true;

        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            setTimeout(() => { // Artificially extend for effect if too fast
                loadingOverlay.style.display = 'none';
                showResult(data);
                analyzeBtn.disabled = false;
            }, 500);
        })
        .catch(error => {
            console.error('Error:', error);
            loadingOverlay.style.display = 'none';
            alert('An error occurred during analysis.');
            analyzeBtn.disabled = false;
        });
    });

    function showResult(data) {
        resultModal.style.display = 'flex';
        
        resultTitle.innerText = data.label;
        resultConfidence.innerText = `Confidence: ${data.confidence}`;
        
        // Reset classes
        resultIcon.className = 'result-icon fas';
        resultModal.querySelector('.modal-content').style.borderColor = '';
        
        if (data.label === 'Real') {
            resultIcon.classList.add('fa-check-circle', 'real-result');
            resultTitle.style.color = '#00ff88';
            resultModal.querySelector('.modal-content').style.borderColor = '#00ff88';
            resultTheory.innerText = "This image's structural patterns, edges, and textures seem perfectly natural, indicating it is an authentic, unaltered photograph.";
        } else {
            resultIcon.classList.add('fa-exclamation-triangle', 'fake-result');
            resultTitle.style.color = '#ff0055';
            resultModal.querySelector('.modal-content').style.borderColor = '#ff0055';
            resultTheory.innerText = "This image features structural anomalies and unnatural patterns often found in AI-generated deepfakes. The texture gradients suggest digital manipulation.";
        }
    }

    // Close Modal
    closeModal.addEventListener('click', () => {
        resultModal.style.display = 'none';
    });

    window.onclick = function(event) {
        if (event.target == resultModal) {
            resultModal.style.display = "none";
        }
    }
});
