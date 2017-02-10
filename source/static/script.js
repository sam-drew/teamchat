$(document).ready(function() {
    messageHandler.start();
    document.getElementById('messageInput').scrollIntoView();
    $("#messageForm").on("submit", function() {
        newMessage($(this));
        return false;
    });
    $("#messageForm").on("keypress", function(e) {
        if (e.keyCode == 13) {
            newMessage($(this));
            return false;
        }
    });
    $("#message").select();
});

function newMessage(input) {
    var message = input.formToDict();
    messageHandler.socket.send(JSON.stringify(message));
    input.find("input[type=text]").val("").select();
};

jQuery.fn.formToDict = function() {
    var fields = this.serializeArray();
    var d = {}
    for (var i = 0; i < fields.length; i++) {
        d[fields[i].name] = fields[i].value;
    }
    if (d.next) delete d.next;
    return d;
};

var messageHandler = {
    socket: null,

    start: function() {
        var url = "ws://" + location.host + "/socket" + location.pathname;
        messageHandler.socket = new WebSocket(url)
        messageHandler.socket.onmessage = function(event) {
            var newMessage = $(JSON.parse(event.data).html);
            $('#messageList').append(newMessage)
            document.getElementById('messageInput').scrollIntoView();
        }
    }
};
