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
function update_chat(data) {
    const sender = data.sender;
    const msg = data.message;

    if (sender === window.userId) {
        add_message(msg)
    } else {
        add_response(msg)
    }

    let messageTimestamp = new Date(data.timestamp);
    console.log(messageTimestamp)
    if (earliestMessageTimestamp === null || messageTimestamp.getTime() < earliestMessageTimestamp.getTime()) {
        console.log("Passed if")
        earliestMessageTimestamp = messageTimestamp;
    }
    console.log(earliestMessageTimestamp)
}



let socket;
$(document).ready(() => {
    scroll_to_end();

    socket = new WebSocket(`ws://127.0.0.1:8000/ws/userchat/${window.conversationId}/`);
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
