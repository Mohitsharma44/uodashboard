//
// Script to grab the image, encode it and return
//

var img = document.getElementById("AudubonCamD6");
var optional_text = document.getElementById("optional_text");
var message_received_once = false;
var arrayBuffer;

var ws = new WebSocket("ws://localhost:8888/realtime");
var $message = $("#message");

ws.binaryType = 'arraybuffer';

ws.onopen = function(){
    $message.attr("class", 'label label-info');
    $message.text("Connecting");
    console.log("connection was established");
    img.src = "/static/imgs/loading.gif";
    img.style.height = '60px';
    img.style.width = '60px';
    img.style.margin = "auto 50%";
    var message = "Connecting to the Live Feed...";
    message = message.fontsize("4").fontcolor("#000000").bold();
    optional_text.innerHTML = message;
    optional_text.style.textAlign="center";
    setTimeout( function(){
	if (!message_received_once){
	    $message.attr("class", 'label label-warning');
	    $message.text('Error');
	    var message = "Connecting to the Live Feed is taking longer than usual.</br>" +
                "Are you sure the cameras are supposed to be streaming ? </br>" +
                "If Yes, then contact: mohit.sharma@nyu.edu";
	    message = message.fontsize("4").fontcolor("#000000").bold();
	    optional_text.innerHTML = message;
	    optional_text.style.textAlign="center";
	}
    }, 20000);
};

ws.onmessage = function(ev){
    var json_data = JSON.parse(ev.data);
    var info = json_data.fname;
    var updatetime = json_data.updatetime;
    arrayBuffer = json_data.img;
    message_received_once = true;
    $message.attr("class", 'label label-success');
    $message.text("Live");
    // Hacky way to remove `b''` from bytes (when serving via python3)
    var teststring = arrayBuffer.substring(0, 2);
    if (teststring === "b'"){
        img.src = "data:image/jpeg;base64," + arrayBuffer.slice(2,-1);
    }
    else{
        img.src = "data:image/jpeg;base64," + arrayBuffer;
    }
    img.style.height = '640px';
    img.style.width = '480px';
    optional_text.innerHTML =
        "Fname: ".bold().fontsize(3) + info + "</br>" +
        "Last updated: ".bold().fontsize(3) + updatetime + "</br>";
};

ws.onclose = function(ev){
    $message.attr("class", 'label label-important');
    $message.text('Not Live');
};

ws.onerror = function(ev){
    $message.attr("class", 'label label-warning');
    $message.text('Error');
    var message = "Could not connect to the Live Feed. <br/> Contact mohit.sharma@nyu.edu";
    message = message.fontsize("4").fontcolor("#000000").bold();
    optional_text.innerHTML = message;
    optional_text.style.textAlign="center";
};
