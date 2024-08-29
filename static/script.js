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


            // Bot message with SQL query results
            const botMsgResult = document.createElement('div');
            botMsgResult.textContent = JSON.stringify(data.result);
            botMsgResult.className = 'chat-bubble bot-message';
            outputDiv.appendChild(botMsgResult);

            // Scroll to the bottom
            outputDiv.scrollTop = outputDiv.scrollHeight;

            // Clear input
            document.getElementById('user-question').value = '';
        }
    })
    .catch(error => console.error('Error:', error));
});
