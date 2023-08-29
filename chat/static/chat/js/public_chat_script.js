const chatType = JSON.parse(document.getElementById('chat-type').textContent);
const roomID = JSON.parse(document.getElementById('chat-id').textContent);
const chatLog = document.querySelector('#chat-log');
const messageInput = document.querySelector('#chat-message-input');
const submitButton = document.querySelector('#submit-button');
const chatInputDiv = document.querySelector('#chat-input');
let publicChatType = null; // канал или группа
let userIsAdmin = null;
let isLoadingStatus = true; // загрузка страницы


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
        case 'initialize':
            console.log('Loading...')
            userIsAdmin = data['is_admin'];
            publicChatType = data['chat_type'];
            if (publicChatType === 1 && !userIsAdmin) { // если чат это channel и пользователь не админ, то удаляем ему поле ввода сообщения, в противном случае оставляем все как есть
                messageInput.remove();
                submitButton.remove();
            }
            isLoadingStatus = false; // убираем загрузку страницы
            console.log('Loading success')
            break
        case 'add_message':
            const div = document.createElement('div');
            div.className = 'message-div';
            div.textContent = `${data.message.sender} - ${data.message.text}`;
            div.id = `message_${data.message.id}`;
            createButtons(div, data.messageId);
            chatLog.append(div);
            console.log('add message');
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
    if (publicChatType == 1 && !userIsAdmin) {
        console.log('сообщения добавлять может только админ')
        return
    }

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
        document.getElementById('label-for-chat-message-input').remove()
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

const createButtons = (div, messageId) => { // создает и помещает кнопки Delete и Edit в переданный div
    if (!userIsAdmin) {
        return
    } 
    const deleteBtn = document.createElement('button');
    deleteBtn.onclick = () => deleteMessage(messageId);
    deleteBtn.textContent = 'Delete message';

    const editBtn = document.createElement('button');
    editBtn.onclick = () => editMessageOnClick(messageId);
    editBtn.textContent = 'Delete message';

    div.append(editBtn)
    div.append(deleteBtn);
}


const deleteMessage = (messageId) => {
    if (publicChatType == 1 && !userIsAdmin) {
        console.log('сообщения удалять может только админ')
        return
    }
    chatSocket.send(JSON.stringify({
        'method': 'delete_message',
        'message_id': messageId,
    }))
};

const editMessageOnClick = (messageId) => {
    if (publicChatType == 1 && !userIsAdmin) {
        console.log('сообщения редактировать может только админ')
        return
    }
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