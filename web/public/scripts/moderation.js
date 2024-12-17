document.addEventListener('DOMContentLoaded', () => {
    const groupInput = document.getElementById('group-id');
    const form = document.getElementById('registration-form');
    const errorMessage = document.getElementById('error-message');

    // Fetch the max group_id from the server
    async function loadMaxGroupId() {
        try {
            const response = await fetch('/api/max-group-id');
            const data = await response.json();

            if (data.max_group_id !== undefined) {
                groupInput.placeholder = `Max group ID: ${data.max_group_id}`;
            }
        } catch (error) {
            console.error('Error loading max group ID:', error);
        }
    }

    // Handle form submission
    form.onsubmit = async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const groupId = groupInput.value;
        const telegramId = document.getElementById('telegram-id').value;
        
        if (!groupId) {
            errorMessage.textContent = 'Please enter a group ID.';
            errorMessage.style.display = 'block';
            return;
        }

        errorMessage.style.display = 'none';

        try {

            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password, telegramId, groupId }),
            });

            if (!response.ok) {
                const error = await response.text();
                throw new Error(error);
            }

            alert('User registered successfully!');
            form.reset();
        } catch (error) {
            console.error('Error registering user:', error);
            errorMessage.textContent = error.message || 'An error occurred.';
            errorMessage.style.display = 'block';
        }
    };

    loadMaxGroupId();
});