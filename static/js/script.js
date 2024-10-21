let conversationStarted = false;

// Function to check and load conversation state from localStorage
function loadConversationState() {
    const state = localStorage.getItem('conversationState');
    if (state) {
        conversationStarted = JSON.parse(state);
    }
}

// Function to save conversation state to localStorage
function saveConversationState() {
    localStorage.setItem('conversationState', JSON.stringify(conversationStarted));
}
function startConversation() {
    fetch('/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log('Start conversation response:', data);
        conversationStarted = data.conversationStarted;
        if (data.response) {
            displayMessage('bot', data.response);
        } else {
            console.error('Unexpected response structure:', data);
        }
        enableChatInput();
        saveConversationState();
    })
    .catch(error => console.error('Error:', error));
}

function sendMessage() {
    const userInput = document.getElementById('userInput').value;
    if (userInput.trim() === '') return;

    displayMessage('user', userInput);
    document.getElementById('userInput').value = '';

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
        console.log('Chat response:', data);
        if (data.error && !data.conversationStarted) {
            startConversation();
        } else if (data.response) {
            displayMessage('bot', data.response);
        } else {
            console.error('Unexpected response structure:', data);
        }
    })
    .catch(error => console.error('Error:', error));
}

function displayMessage(sender, message) {
    console.log('Displaying message:', sender, message);
    const chatBox = document.getElementById('messages');
    if (!chatBox) {
        console.error('Chat box element not found!');
        return;
    }

    const messageElement = document.createElement('div');
    messageElement.classList.add(sender.toLowerCase());
    
    // Check if message is an object and has a 'response' property
    if (typeof message === 'object' && message.response) {
        message = message.response;
    }
    
    messageElement.textContent = `${sender}: ${message}`;
    chatBox.appendChild(messageElement);

    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
}

function enableChatInput() {
    document.getElementById('userInput').disabled = false;
}

// Function to reset the conversation state
function resetConversation() {
    conversationStarted = false; // Reset the conversation state
    document.getElementById('messages').innerHTML = ''; // Clear chat messages
    document.getElementById('userInput').disabled = true; // Disable input until conversation starts
    startConversation(); // Start a new conversation
    saveConversationState(); // Save the new state
}

// Function to end the conversation
function endConversation() {
    conversationStarted = false;
    saveConversationState(); // Save the updated state
    document.getElementById('userInput').disabled = true; // Disable the input
}

// Call this when the page loads
document.addEventListener('DOMContentLoaded', (event) => {
    loadConversationState(); // Load the conversation state when the page loads
    if (conversationStarted) {
        startConversation(); // Optionally restart conversation if state is true
    }
});

