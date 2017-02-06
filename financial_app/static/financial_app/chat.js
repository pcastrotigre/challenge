$(function() {
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var socket = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);
    
    socket.onmessage = function(message) {
        var data = JSON.parse(message.data);
        $('#chat-msg').val('');
        if(data.username == $('#username').val()){
            $('#msg-list').append('<li class="text-right list-group-item">' + data.message + '</li>');
        }
        else{
            $('#msg-list').append('<li class="text-left list-group-item">' + data.message + '</li>');   
        }
        var chatlist = document.getElementById('msg-list-div');
        chatlist.scrollTop = chatlist.scrollHeight;
    };


    $("#chat-form").on("submit", function(event) {
        var message = {
            username: $('#username').val(),
            message: $('#chat-msg').val(),
        }
        socket.send(JSON.stringify(message));
        $("#chat-msg").val('').focus();
        return false;
    });
});