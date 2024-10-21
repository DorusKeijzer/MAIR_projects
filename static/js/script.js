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
        conversationStarted = data.conversationStarted;
        displayMessages(data.messages);
        enableChatInput();
        saveConversationState(); // Save state after starting conversation
    })
    .catch(error => console.error('Error:', error));
}

function sendMessage() {
    const userInput = document.getElementById('userInput').value;
    if (userInput.trim() === '') return;

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
        if (data.error && !data.conversationStarted) {
            startConversation();
        } else {
            displayMessages(data.messages);
        }
    })
    .catch(error => console.error('Error:', error));
}

function displayMessages(messages) {
    const chatBox = document.getElementById('messages');
    if (!chatBox) {
        console.error('Chat box element not found!');
        return;
    }

    chatBox.innerHTML = ''; // Clear existing messages

    messages.forEach(([sender, message]) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add(sender);
        messageElement.textContent = `${sender}: ${message}`;
        chatBox.appendChild(messageElement);
    });

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

