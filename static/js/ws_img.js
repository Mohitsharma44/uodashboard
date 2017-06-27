//
// Script to grab the image, encode it and return
//
// http://stackoverflow.com/questions/22554313/send-captured-images-from-python-server-to-javascript-client

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
    img.src = "images/connecting.svg"
    img.style.height = '60px';
    img.style.width = '60px';
    img.style.margin = "0 auto";
    var message = "Connecting to the Live Feed can take upto 20 seconds."
    message = message.fontsize("4").fontcolor("#000000").bold();
    optional_text.innerHTML = message;
    optional_text.style.textAlign="center";
    setTimeout( function(){
	if (!message_received_once){
	    $message.attr("class", 'label label-warning');
	    $message.text('Error');
	    var message = "Could not connect to the Live Feed. <br/> Contact mohit.sharma@nyu.edu"
	    message = message.fontsize("4").fontcolor("#000000").bold();
	    optional_text.innerHTML = message;
	    optional_text.style.textAlign="center";
	}
    }, 20000);
};

ws.onmessage = function(evt){
    arrayBuffer = evt.data;
    console.log("Got something");
    message_received_once = true;
    $message.attr("class", 'label label-success')
    $message.text("Live")
    img.src = "data:image/jpeg;base64," + encode(new Uint8Array(arrayBuffer));
    //img.src = "data:image/jpeg;base64," + encode(new Uint8Array(arrayBuffer));
    img.style.height = '700px';
    img.style.width = '900px';
    optional_text.innerHTML = "";
};

function encode (input) {
    var keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    var output = "";
    var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
    var i = 0;

    while (i < input.length) {
	chr1 = input[i++];
	chr2 = i < input.length ? input[i++] : Number.NaN; // Not sure if the index
	chr3 = i < input.length ? input[i++] : Number.NaN; // checks are needed here

	enc1 = chr1 >> 2;
	enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
	enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
	enc4 = chr3 & 63;

	if (isNaN(chr2)) {
	    enc3 = enc4 = 64;
	} else if (isNaN(chr3)) {
	    enc4 = 64;
	}
	output += keyStr.charAt(enc1) + keyStr.charAt(enc2) +
	    keyStr.charAt(enc3) + keyStr.charAt(enc4);
    }
    return output;
}

ws.onclose = function(ev){
    $message.attr("class", 'label label-important');
    $message.text('Not Live');
};
ws.onerror = function(ev){
    $message.attr("class", 'label label-warning');
    $message.text('Error');
    var message = "Could not connect to the Live Feed. <br/> Contact mohit.sharma@nyu.edu"
    message = message.fontsize("4").fontcolor("#000000").bold();
    optional_text.innerHTML = message;
    optional_text.style.textAlign="center";
};
