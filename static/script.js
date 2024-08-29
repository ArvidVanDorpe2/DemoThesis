document.getElementById('ask-button').addEventListener('click', function() {
    const userQuestion = document.getElementById('user-question').value;

    if (!userQuestion.trim()) {
        alert("Please enter a question.");
        return;
    }

    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'question=' + encodeURIComponent(userQuestion)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            const outputDiv = document.getElementById('chat-output');

            // User message
            const userMsg = document.createElement('div');
            userMsg.textContent = userQuestion;
            userMsg.className = 'chat-bubble user-message';
            outputDiv.appendChild(userMsg);


            // Bot message with interpreted answer
            const botMsgAnswer = document.createElement('div');
            botMsgAnswer.textContent = data.interpreted_result;
            botMsgAnswer.className = 'chat-bubble bot-message';
            outputDiv.appendChild(botMsgAnswer);

            // Scroll to the bottom
            outputDiv.scrollTop = outputDiv.scrollHeight;

            // Clear input
            document.getElementById('user-question').value = '';
        }
    })
    .catch(error => console.error('Error:', error));
});
