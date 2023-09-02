const chatType = JSON.parse(document.getElementById('chat-type').textContent);
const roomID = JSON.parse(document.getElementById('chat-id').textContent);
const userUsername = JSON.parse(document.getElementById('user-username').textContent);
const chat = document.querySelector('.chat-wrapper');
const messageInput = document.querySelector('.chat-input');
const submitButton = document.querySelector('.chat-send-btn');
const chatInputDiv = document.querySelector('.chat-input-wrapper');
let editMessageID = null

chat.scrollTo(0, chat.scrollHeight)

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
    const messageDiv = document.getElementById(`message_${data.message_id}`);
    switch (data.method) {
        case 'add_message':
            const messageWrapper = document.createElement('div');
            messageWrapper.id = `message_${data.message.id}`
            messageWrapper.className = 'message-wrapper';

            const img = document.createElement('img');
            img.className = 'message-pp';
            img.alt = 'profile-pic';

            const messageEditDel = document.createElement('div');
            messageEditDel.className = 'message-edit-del'
            if (data.message.sender === userUsername) {
                messageWrapper.className += ' reverse'
                img.src = 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=2550&q=80';
                const editSpan = document.createElement('span');
                editSpan.onclick = () => editMessageOnClick(data.message.id);
                editSpan.textContent = 'edit '
                messageEditDel.appendChild(editSpan)
            } else {
                img.src = 'https://images.unsplash.com/photo-1587080266227-677cc2a4e76e?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&amp;ixlib=rb-1.2.1&amp;auto=format&amp;fit=crop&amp;w=934&amp;q=80'
            }

            messageWrapper.appendChild(img)
            const messageBoxWrapper = document.createElement('div');

            messageBoxWrapper.className = 'message-box-wrapper'
            const messageBox = document.createElement('div');
            messageBox.className = 'message-box'

            messageBox.textContent = data.message.text

            messageBoxWrapper.appendChild(messageBox)
            const divTime = document.createElement('div');
            divTime.style.userSelect = 'none'

            const spanEdited = document.createElement('span');
            spanEdited.hidden = true
            spanEdited.textContent = 'edited '
            divTime.appendChild(spanEdited)

            const spanTime = document.createElement('span');
            spanTime.textContent = data.message.time_create
            divTime.appendChild(spanTime)

            messageBoxWrapper.appendChild(divTime)

            const delSpan = document.createElement('span');
            delSpan.onclick = () => deleteMessage(data.message.id);
            delSpan.textContent = 'delete'
            messageEditDel.appendChild(delSpan)

            messageBoxWrapper.appendChild(messageEditDel)
            messageWrapper.appendChild(messageBoxWrapper)
            chat.appendChild(messageWrapper)
            chat.scrollTo(0, chat.scrollHeight)
            break;
        case 'delete_message':
            messageDiv.remove();
            break;
        case 'edit_message':
            messageDiv.querySelector("div > div.message-box").textContent = data.text;
            messageDiv.querySelector("div > div:nth-child(2) > span:nth-child(1)").hidden = false
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
    if (messageInput.value.trim().length === 0) return

    if (editMessageID) {
        chatSocket.send(JSON.stringify({
            'method': 'edit_message',
            'message_id': editMessageID,
            'text': messageInput.value,
        }))
        messageInput.removeEventListener('input', editMessageListener)
        editMessageID = null
        submitButton.textContent = 'Send';
    } else {
        chatSocket.send(JSON.stringify({
            'method': 'add_message',
            'text': messageInput.value,
        }));
    }

    messageInput.value = '';
    messageInput.focus();
};

clearInput = (e) => {
    messageInput.value = ''
    messageInput.focus();
    editMessageID = null
    submitButton.textContent = 'Send';
}

const deleteMessage = (messageId) => {
    chatSocket.send(JSON.stringify({
        'method': 'delete_message',
        'message_id': messageId,
    }))
};

const editMessageListener = function () {
    document.querySelector(`#message_${editMessageID} > div > div.message-box`).innerText = this.value;
}

const editMessageOnClick = (messageId) => {
    editMessageID = messageId
    messageInput.value = document.querySelector(`#message_${editMessageID} > div > div.message-box`).textContent.trim();

    messageInput.addEventListener('input', editMessageListener)
    messageInput.focus();
    submitButton.textContent = 'Edit';
};