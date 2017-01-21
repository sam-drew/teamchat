var messageHandler = {
    socket: null;

    start: function() {
        var url = "ws://" + location.host + "/socket" + location.pathname;
        messageHandler.socket = new WebSocket(url)
        messageHandler.socket.onmessage = function(event) {
            messageHandler.addMessage(JSON.parse(event.data));
        }
    },

    addMessage: function(message) {
        var present = $('#message' + message.id)
        if (present.length > 0) return;
        var newMessage = $(message.html);
        $('#messageList').append(newMessage)
    }
}
