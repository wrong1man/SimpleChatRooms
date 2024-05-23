function add_response(text){
    let div_wrap;
    if (!$(".ps-container").children().last().hasClass("media-chat-reverse") && $(".ps-container").children().last().hasClass("media-chat")){
        div_wrap = $(".ps-container").children().last()
    } else {
        div_wrap = $(`<div class="media media-chat"></div>`)
        div_wrap.append($(`<div class="media-body"></div>`))
        $(".ps-container").append(div_wrap)
    }
    $(div_wrap).find(".media-body").append(`<p>${text}</p>`)
    scroll_to_end()
}

function add_message(text){
    let div_wrap;
    if ($(".ps-container").children().last().hasClass("media-chat-reverse")){
        div_wrap = $(".ps-container").children().last()
    } else {
        div_wrap = $(`<div class="media media-chat media-chat-reverse"></div>`)
        div_wrap.append($(`<div class="media-body"></div>`))
        $(".ps-container").append(div_wrap)
    }
    $(div_wrap).find(".media-body").append(`<p>${text}</p>`)
    scroll_to_end()
}

function scroll_to_end(){
    const d = $('.ps-container')
    d.scrollTop(d.prop("scrollHeight"))
}

function send_message() {
    const msg = $("#written_message").val();
    if (msg !== "") {
        socket.send(JSON.stringify({
            'message': msg
        }));
    };
    $("#written_message").val('');
}

let earliestMessageTimestamp = new Date();
function update_chat_old(data) {
    const sender = data.sender;
    const msg = data.message;

    if (sender === window.userId) {
        add_message(msg)
    } else {
        add_response(msg)
    }

    let messageTimestamp = new Date(data.timestamp);
    if (earliestMessageTimestamp === null || messageTimestamp.getTime() < earliestMessageTimestamp.getTime()) {
        earliestMessageTimestamp = messageTimestamp;
    }
}
function prepend_message(text, isResponse){
    let div_wrap;
    let messageClass = isResponse ? "media media-chat" : "media media-chat media-chat-reverse";

    if ($("#load_previous_host").next()[0].classList == messageClass) {
        div_wrap = $("#load_previous_host").next();
    } else {
        div_wrap = $(`<div class="${messageClass}"></div>`);
        div_wrap.append($(`<div class="media-body"></div>`));
        $("#load_previous_host").after(div_wrap);
    }

    $(div_wrap).find(".media-body").prepend(`<p>${text}</p>`);
}

function update_chat(data, prepend) {
    if (data.hasOwnProperty("error")){
        alert(data.error);
        return
    }

    const sender = data.sender;
    const msg = data.message;

    if (prepend) {
        prepend_message(msg, sender !== window.userId);
    } else {
        if (sender === window.userId) {
            add_message(msg)
        } else {
            add_response(msg)
        }
    }

    let messageTimestamp = new Date(data.timestamp);
    if (earliestMessageTimestamp === null || messageTimestamp.getTime() < earliestMessageTimestamp.getTime()) {
        earliestMessageTimestamp = messageTimestamp;
    }
}


let socket;
// const SITE_LINK = "127.0.0.1:8000"
const SITE_LINK = "sograpp.com"
$(document).ready(() => {
    scroll_to_end();

    socket = new WebSocket(`ws://${SITE_LINK}/ws/userchat/${window.conversationId}/`);
    socket.onmessage = (e) => {
        update_chat(JSON.parse(e.data));
    };
    socket.onerror = (error) => {
        console.error(`WebSocket error: ${error}`);
    }

    $("#written_message").keypress((e) => {
        if (e.which === 13) {  // 13 is the keycode for the "Enter" key
            e.preventDefault();
            send_message();
        }

    });
})
function loadPreviousMessages() {
    // Convert the timestamp to the format your backend expects
    const timestampStr = earliestMessageTimestamp.toISOString();

    // Make a GET request to your backend
    fetch(`/load_previous_messages/?timestamp=${timestampStr}&cid=${window.conversationId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(messages => {
            // Handle the response
            // Update `earliestMessageTimestamp` if necessary
            if (messages.length ==0){
                alert("No previous messages found.")
            }
            messages.forEach((item) => {
                const message = {
                    sender: item.fields.sender,
                    message: item.fields.content,
                    timestamp: item.fields.timestamp
                };
                update_chat(message, true);  // Pass true for the prepend parameter
            });
        })
        .catch(error => {
            console.error(`Error loading previous messages: ${error}`);
        });
}
