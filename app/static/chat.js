var current_chat_friend_name = null

function createMessageHTML(message) {
    const is_friend = message.sender === current_chat_friend_name;

    if (is_friend){
        return `
            <div class="message-container-right">
                <h3 class="message-text">
                    ${message.sender}: ${message.content} 
                </h3>
            </div>
        `;
    }

    else{
        return `
            <div class="message-container-left">
                <h3 class="message-text">
                    ${message.sender}: ${message.content} 
                </h3>
            </div>
        `;

    }
}

function messenger_scroll_down(){
    setTimeout(function() {
        const messages_element = document.getElementsByClassName("messenger-messages")[0];
        messages_element.scrollTo({
            top: messages_element.scrollHeight,
            behavior: 'smooth'
        })
    },100)
}

function init_chat_socket(){
    if (typeof socket !== 'undefined') {
        socket.on('new_message', function(data) {
            
            if (data.sender === current_chat_friend_name) {
                const messageHTML = createMessageHTML(data);
                document.getElementById('messenger-messages').insertAdjacentHTML('beforeend', messageHTML);
                messenger_scroll_down();
            }
        });
    }
    else{
        setTimeout(init_chat_socket, 100)
    }
}
init_chat_socket()
