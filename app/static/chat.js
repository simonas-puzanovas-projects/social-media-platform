var current_chat_friend_name = null

function createMessageHTML(message) {
    const isCurrentUser = message.sender === current_chat_friend_name;
    const color = isCurrentUser ? 'orange' : 'yellow';
    const align = isCurrentUser ? 'right' : 'left';

    return `
        <div>
            <h3 class="message-text" style="color: ${color}; text-align: ${align};">
                ${message.sender}: ${message.content}
            </h3>
        </div>
    `;
}

function init_chat_socket(){
    if (typeof socket !== 'undefined') {
        socket.on('new_message', function(data) {
            
            if (data.sender === current_chat_friend_name) {
                const messageHTML = createMessageHTML(data);
                document.getElementById('chat-messages').insertAdjacentHTML('beforeend', messageHTML);
            }
        });
    }
    else{
        setTimeout(init_chat_socket, 50)
    }
}

init_chat_socket()