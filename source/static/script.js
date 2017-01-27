$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

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
    messageHandler.start();
});

function newMessage(input) {
    var message = input.formToDict();
    messageHandler.socket.send(JSON.stringify(message));
    input.find("input[type=text]").val("").select();
};

jQuery.fn.formToDict = function() {
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

var messageHandler = {
    socket: null,

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
};
