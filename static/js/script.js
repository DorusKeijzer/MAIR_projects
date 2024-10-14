let conversationStarted = false;

function startConversation() {
    fetch('/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        conversationStarted = data.conversationStarted;
        displayMessage(data.response, 'bot');
        enableChatInput();
    })
    .catch(error => console.error('Error:', error));
}

function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === '') return;

    displayMessage(userInput, 'user');
    document.getElementById('user-input').value = '';

    if (!conversationStarted) {
        startConversation();
        return;
    }

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error && !data.conversationStarted) {
            startConversation();
        } else {
            displayMessage(data.response, 'bot');
        }
    })
    .catch(error => console.error('Error:', error));
}
function displayMessage(message, sender) {
    const chatBox = document.getElementById('messages');
    if (!chatBox) {
        console.error('Chat box element not found!');
        return;
    }

    const messageElement = document.createElement('div');
    messageElement.classList.add(sender);
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function enableChatInput() {
    document.getElementById('user-input').disabled = false;
    document.getElementById('send-button').disabled = false;
}

// Call this when the page loads
document.addEventListener('DOMContentLoaded', (event) => {
    startConversation();
});

