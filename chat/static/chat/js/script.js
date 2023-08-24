const chatType = JSON.parse(document.getElementById('chat-type').textContent);
const roomID = JSON.parse(document.getElementById('chat-id').textContent);
const chatLog = document.querySelector('#chat-log');
const messageInput = document.querySelector('#chat-message-input');
const submitButton = document.querySelector('#submit-button');
const chatInputDiv = document.querySelector('#chat-input');

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/'
    + chatType
    + '/'
    + roomID
    + '/'
);

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(data);
    switch (data.method) {
        case 'add_message':
            const div = document.createElement('div');
            div.className = 'message-div';
            div.textContent = `${data.message.sender} - ${data.message.text}`;
            div.id = `message_${data.message.id}`;
            const btn = document.createElement('button');
            btn.onclick = () => deleteMessage(data.message.id);
            btn.textContent = 'Delete message';
            div.append(btn);
            chatLog.append(div);
            console.log('method work');
            break;
        case 'delete_message':
            const messageDiv = document.getElementById(`message_${data.message_id}`);
            messageDiv.remove();
            break;
        case 'edit_message':
            const messageSpan = document.getElementById(`message_${data.message_id}`).querySelector('span:nth-child(2)');
            messageSpan.textContent = data.text;
            break;
        default:
            console.log('Method is not provided');
    }
};

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};

messageInput.focus();

messageInput.onkeyup = function (e) {
    if (e.key === 'Enter') {
        submitButton.click();
    }
};

submitButtonOnClick = (e) => {
    if (messageInput.value.trim().length === 0) {
        alert("Message cannot be blank");
        messageInput.focus();
    }

    const editedMessageId = submitButton.getAttribute('edit-message-id');

    if (editedMessageId) {
        chatSocket.send(JSON.stringify({
            'method': 'edit_message',
            'message_id': editedMessageId,
            'text': messageInput.value,
        }))
        submitButton.removeAttribute('edit-message-id');
        submitButton.textContent = 'Send';
    } else {
        chatSocket.send(JSON.stringify({
            'method': 'add_message',
            'text': messageInput.value,
        }));
    }
    ;

    messageInput.value = '';
    messageInput.focus();
};

const deleteMessage = (messageId) => {
    chatSocket.send(JSON.stringify({
        'method': 'delete_message',
        'message_id': messageId,
    }))
};

const editMessageOnClick = (messageId) => {
    console.log('editMessageOnClick');
    const label = document.createElement('label');
    label.for = 'chat-message-input';
    label.id = 'label-for-chat-message-input';
    label.textContent = 'Редактирование';
    chatInputDiv.append(label);
    messageInput.value = document.getElementById(`message_${messageId}`).querySelector('span:nth-child(2)').textContent;
    messageInput.focus();
    submitButton.setAttribute('edit-message-id', messageId);
    submitButton.textContent = 'Edit';
};