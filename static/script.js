document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('checker-form');
    const textInput = document.getElementById('text-input');
    const fileUpload = document.getElementById('file-upload');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = document.getElementById('loading-spinner');
    const errorMsg = document.getElementById('error-message');
    const resultsSection = document.getElementById('results-section');
    const scoreCircle = document.getElementById('score-circle');
    const scoreText = document.getElementById('score-text');
    const verdictText = document.getElementById('verdict-text');
    const detailsList = document.getElementById('details-list');

    // Theme Switch Logic
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    const currentTheme = localStorage.getItem('theme');

    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        if (currentTheme === 'dark') toggleSwitch.checked = true;
    }

    toggleSwitch.addEventListener('change', function (e) {
        if (e.target.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    });

    // File Upload Logic
    fileUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                textInput.value = e.target.result;
            };
            reader.readAsText(file);
        }
    });

    // Form Submit Logic
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const text = textInput.value.trim();
        if (!text) {
            showError('Please enter some text to check.');
            return;
        }

        setLoadingState(true);
        hideError();
        resultsSection.classList.add('hidden');

        try {
            const token = localStorage.getItem('jwtToken');
            if (!token) {
                window.location.href = '/login';
                return;
            }

            const response = await fetch('/check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ text })
            });

            const data = await response.json();

            if (response.status === 401) {
                localStorage.removeItem('jwtToken');
                window.location.href = '/login';
                return;
            }

            if (!response.ok) {
                throw new Error(data.error || 'Something went wrong');
            }

            displayResults(data);
        } catch (error) {
            showError(error.message);
        } finally {
            setLoadingState(false);
        }
    });

    function setLoadingState(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.textContent = 'Checking...';
            spinner.classList.remove('hidden');
        } else {
            submitBtn.disabled = false;
            btnText.textContent = 'Check Plagiarism';
            spinner.classList.add('hidden');
        }
    }

    function showError(message) {
        errorMsg.textContent = message;
        errorMsg.classList.remove('hidden');
    }

    function hideError() {
        errorMsg.classList.add('hidden');
    }

    function displayResults(data) {
        const sim = data.similarity;
        resultsSection.classList.remove('hidden');

        // Update score circle
        scoreCircle.setAttribute('stroke-dasharray', `${sim}, 100`);
        scoreText.textContent = `${sim}%`;

        // Color coding based on similarity
        let colorClass = 'success-text';
        let strokeColor = 'var(--success-color)';
        let verdict = 'Looking Good! Original Content.';

        if (sim > 70) {
            colorClass = 'danger-text';
            strokeColor = 'var(--error-color)';
            verdict = 'High Plagiarism Detected!';
        } else if (sim > 30) {
            colorClass = 'warning-text';
            strokeColor = 'var(--warning-color)';
            verdict = 'Moderate Similarity Found.';
        }

        scoreCircle.style.stroke = strokeColor;
        verdictText.textContent = verdict;
        verdictText.className = 'verdict ' + colorClass;
        scoreText.className = 'percentage ' + colorClass;

        // Details List Update
        detailsList.innerHTML = '';
        if (Object.keys(data.details).length === 0) {
            detailsList.innerHTML = '<li style="justify-content:center;">No stored documents available to compare.</li>';
        } else {
            for (let [doc, score] of Object.entries(data.details)) {
                const li = document.createElement('li');

                let docColorClass = 'success-bg';
                if (score > 70) docColorClass = 'danger-bg';
                else if (score > 30) docColorClass = 'warning-bg';

                li.innerHTML = `
                    <span class="doc-name">${doc}</span>
                    <span class="doc-score ${docColorClass}">${score}% Match</span>
                `;
                detailsList.appendChild(li);
            }
        }

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
});
