
function startConversation() {
  // Start the conversation and get the initial message
  fetch('/start', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => {
    appendMessage('Bot', data.response);
  });
}

function sendMessage() {
  const input = document.getElementById('userInput').value;
  if (input.trim() !== "") {
    appendMessage('You', input);

    // Send input to backend
    fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: input })
    })
    .then(response => response.json())
    .then(data => {
      appendMessage('Bot', data.response);
    });

    // Clear input field
    document.getElementById('userInput').value = '';
  }
}

function appendMessage(sender, message) {
  const messagesDiv = document.getElementById('messages');
  const newMessage = document.createElement('div');
  newMessage.className = 'message';
  newMessage.innerHTML = `<strong>${sender}:</strong> ${message}`;
  messagesDiv.appendChild(newMessage);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;  // Auto scroll to the bottom
}

