let conversationStarted = false;
let userId = null;



document.addEventListener('DOMContentLoaded', (event) => {
    loadConversationState();
    starConversation();
});

function loadConversationState() {
    const state = localStorage.getItem('conversationState');
    if (state) {
        const parsedState = JSON.parse(state);
        conversationStarted = parsedState.conversationStarted;
        userId = parsedState.userId;
    }
}

function saveConversationState() {
    localStorage.setItem('conversationState', JSON.stringify({
        conversationStarted,
        userId
    }));
}

function extractMessageContent(messageObj) {
    if (!messageObj) return '';
    
    // If it's already a string, return it directly
    if (typeof messageObj === 'string') {
        return messageObj;
    }
    
    // Handle object with response array
    if (messageObj.response && Array.isArray(messageObj.response)) {
        return messageObj.response[0] || '';
    }
    
    // Handle responses array
    if (messageObj.responses && typeof messageObj.responses === 'string') {
        return messageObj.responses;
    }
    
    // Handle array
    if (Array.isArray(messageObj)) {
        return messageObj[1] || messageObj[0] || '';
    }
    
    // If we can't extract content, return empty string
    return '';
}
function startConversation() {
    fetch('/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            preference_mode: window.PREFERENCE_MODE || 'default'
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Start conversation response:', data);
        conversationStarted = data.conversationStarted;
        userId = data.user_id;
        
        if (data.data && Array.isArray(data.data.messages)) {
            data.data.messages.forEach(message => {
                const content = extractMessageContent(message.content);
                displayMessage(message.sender, content);
            });
        }
        
        enableChatInput();
        saveConversationState();
    })
    .catch(error => console.error('Error starting conversation:', error));
}

function sendMessage() {
    const userInput = document.getElementById('userInput').value;
    if (userInput.trim() === '') return;

    displayMessage('user', userInput);
    document.getElementById('userInput').value = '';

    if (conversationStarted) {
        sendChatMessage(userInput);
    }
}

function sendChatMessage(userInput) {
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput, user_id: userId }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Chat response:', data);
        
        if (data.error && !data.conversationStarted) {
            startConversation();
        } else if (data.data && Array.isArray(data.data.messages)) {
            const newMessages = data.data.messages;
            const lastBotMessage = newMessages.filter(msg => msg.sender === 'bot').pop();
            if (lastBotMessage) {
                const content = extractMessageContent(lastBotMessage.content);
                displayMessage(lastBotMessage.sender, content);
            }
        } else {
            console.error('Unexpected response structure:', data);
        }
    })
    .catch(error => console.error('Error sending chat message:', error));
}

function resetConversation() {
    conversationStarted = false;
    userId = null;
    document.getElementById('messages').innerHTML = '';
    document.getElementById('userInput').disabled = true;
    startConversation();
    saveConversationState();
}

function endConversation() {
    fetch('/end', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('End conversation response:', data);
        conversationStarted = false;
        userId = null;
        saveConversationState();
        document.getElementById('userInput').disabled = true;
    })
    .catch(error => console.error('Error ending conversation:', error));
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
    messageElement.textContent = `${sender}: ${message}`;
    chatBox.appendChild(messageElement);

    chatBox.scrollTop = chatBox.scrollHeight;
}

function enableChatInput() {
    document.getElementById('userInput').disabled = false;
}


document.addEventListener('DOMContentLoaded', (event) => {
    loadConversationState();
    startConversation();

    // Add keypress event listener for the user input
    const userInputElement = document.getElementById('userInput');
    userInputElement.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent the default action of the Enter key
            sendMessage(); // Call the sendMessage function
        }
    });
});

