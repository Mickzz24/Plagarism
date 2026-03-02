document.addEventListener('DOMContentLoaded', () => {
    // Theme Switch Logic (Reusable)
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    const currentTheme = localStorage.getItem('theme');

    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        if (currentTheme === 'dark') {
            if (toggleSwitch) toggleSwitch.checked = true;
        }
    }

    if (toggleSwitch) {
        toggleSwitch.addEventListener('change', function (e) {
            if (e.target.checked) {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
            }
        });
    }

    const signupForm = document.getElementById('signup-form');
    const loginForm = document.getElementById('login-form');
    const authErrorMsg = document.getElementById('auth-error-message');
    const authSuccessMsg = document.getElementById('auth-success-message');

    function showAuthError(message) {
        if (authSuccessMsg) authSuccessMsg.classList.add('hidden');
        authErrorMsg.textContent = message;
        authErrorMsg.classList.remove('hidden');
    }

    function showAuthSuccess(message) {
        if (authErrorMsg) authErrorMsg.classList.add('hidden');
        authSuccessMsg.textContent = message;
        authSuccessMsg.classList.remove('hidden');
    }

    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('signup-btn');
            const spinner = document.getElementById('signup-spinner');
            const btnText = btn.querySelector('.btn-text');
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;

            if (!username || !password) {
                showAuthError("Please provide both username and password.");
                return;
            }

            btn.disabled = true;
            spinner.classList.remove('hidden');
            btnText.textContent = "Creating...";

            try {
                const response = await fetch('/api/signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Failed to sign up');
                }

                showAuthSuccess("Account created successfully! Redirecting to login...");
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);

            } catch (error) {
                showAuthError(error.message);
                btn.disabled = false;
                spinner.classList.add('hidden');
                btnText.textContent = "Sign Up";
            }
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('login-btn');
            const spinner = document.getElementById('login-spinner');
            const btnText = btn.querySelector('.btn-text');
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;

            if (!username || !password) {
                showAuthError("Please provide both username and password.");
                return;
            }

            btn.disabled = true;
            spinner.classList.remove('hidden');
            btnText.textContent = "Signing In...";

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Invalid credentials');
                }

                localStorage.setItem('jwtToken', data.token);
                window.location.href = '/'; // Redirect to main app

            } catch (error) {
                showAuthError(error.message);
                btn.disabled = false;
                spinner.classList.add('hidden');
                btnText.textContent = "Sign In";
            }
        });
    }
});
