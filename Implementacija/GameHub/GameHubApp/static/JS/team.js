/* Author: Mihajlo Blagojevic 0283/2021 */

document.addEventListener("DOMContentLoaded", function () {
    let messages_div = document.getElementById('div_messages');
    messages_div.scrollTo(0, messages_div.scrollHeight);

    // Name of the room, generated in function team
    const roomName = JSON.parse(document.getElementById('room-name').textContent);

    const chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/chat/'
        + roomName
        + '/'
    );

    // Receive message from the room
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        let text = data.message
        let id_user_sent_msg = data.id_user_sent_msg
        let username_user_sent_msg = data.username_user_sent_msg
        let link_user_that_sent_msg = data.link_user
        let same_user_as_prev_mess = data.same_user_as_prev_mess
        let is_my_message = data.is_my_message

        let new_msg = create_message(text, id_user_sent_msg, username_user_sent_msg,
                                     link_user_that_sent_msg, is_my_message, same_user_as_prev_mess)
        document.querySelector('#div_messages').appendChild(new_msg);
        messages_div.scrollTo(0, messages_div.scrollHeight);
    };

    // Send a message to the room
    document.querySelector('#message_button').onclick = function(e) {
        const messageInputDom = document.querySelector('#message_input');
        let message = messageInputDom.value;
        if (message === "")
            return
        if(message.length > 2000)
            message = message.substring(0, 2000)
        chatSocket.send(JSON.stringify({
            'message': message,
            'room_name': roomName
        }));
        messageInputDom.value = '';
    };

    // Create a message
    function create_message(text, id_user_that_sent_msg, username_user_that_sent_msg,
                            link_user_that_sent_msg, is_my_message, same_user_as_prev_mess){
        let msg = document.createElement("div")
        let div_body = document.createElement("div")
        div_body.classList.add("body")
        msg.appendChild(div_body)

        let span = document.createElement("span")
        span.innerHTML = text
        if (is_my_message === true){
            msg.classList.add("my-message")
        }
        else{
            msg.classList.add("message")
            if (same_user_as_prev_mess === false) {
                let a_link_user = document.createElement("a")
                a_link_user.classList.add("username")
                a_link_user.href = link_user_that_sent_msg
                a_link_user.text = username_user_that_sent_msg
                div_body.appendChild(a_link_user)
            }
        }
        div_body.appendChild(span)
        return msg
    }

    chatSocket.onclose = function(e) { console.error('Chat socket closed unexpectedly'); };

    document.querySelector('#message_input').onkeyup = function(e) {
        if (e.key === 'Enter') {
            document.querySelector('#message_button').click();
        }
    };
});
