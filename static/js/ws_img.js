//
// Script to grab the image, encode it and return
//
//var pre_panel_img = document.getElementById("AudubonCamD9");
var pre_panel_text = document.getElementById("pre_panel_text");
var d6img = document.getElementById("AudubonCamD6");
var d9img = document.getElementById("AudubonCamD9");
var optional_d6_text = document.getElementById("optional_d6_text");
var optional_d9_text = document.getElementById("optional_d9_text");
var message_received_once = false;
var arrayBuffer;
var img_height = '372px';
var img_width = '544px';
var ws = new WebSocket("ws://localhost:8888/realtime");
var $message = $("#message");

ws.binaryType = 'arraybuffer';

ws.onopen = function(){
    $message.attr("class", 'label label-info');
    $message.text("Connecting");
    console.log("connection was established");
    d6img.src = "/static/imgs/loading.gif";
    d9img.src = "/static/imgs/loading.gif";
    d6img.style.height = '50px';
    d9img.style.height = '50px';
    d6img.style.width = '60px';
    d9img.style.width = '60px';
    d6img.style.margin = "auto 50%";
    d9img.style.margin = "auto 50%";
    var message = "Connecting to the Live Feed...";
    message = message.fontsize("4").fontcolor("#000000").bold();
    pre_panel_text.innerHTML = message;
    pre_panel_text.style.textAlign="center";
    setTimeout( function(){
	if (!message_received_once){
	    $message.attr("class", 'label label-warning');
	    $message.text('Error');
	    var message = "Connecting to the Live Feed is taking longer than usual.</br>" +
                "Are you sure the cameras are supposed to be streaming ? </br>" +
                "If Yes, then contact: mohit.sharma@nyu.edu";
	    message = message.fontsize("4").fontcolor("#000000").bold();
	    pre_panel_text.innerHTML = message;
	    pre_panel_text.style.textAlign="center";
	}
    }, 20000);
};

ws.onmessage = function(ev){
    var json_data = JSON.parse(ev.data);
    var info = json_data.fname;
    var updatetime = json_data.updatetime;
    var cam_name = json_data.cam_name;
    arrayBuffer = json_data.img;
    message_received_once = true;
    $message.attr("class", 'label label-success');
    $message.text("Live");
    // Set the image based on tag
    if (cam_name === "d6"){
        // Hacky way to remove `b''` from bytes (when serving via python3)
        var teststring = arrayBuffer.substring(0, 2);
        if (teststring === "b'"){
            d6img.src = "data:image/jpeg;base64," + arrayBuffer.slice(2,-1);
        }
        else{
            d6img.src = "data:image/jpeg;base64," + arrayBuffer;
        }
        d6img.style.height = img_height;
        d6img.style.width = img_width;
        d6img.style.margin = "0 auto";
        optional_d6_text.innerHTML =
            "File name: ".bold().fontsize(3) + info + "</br>" +
            "Last updated: ".bold().fontsize(3) + updatetime ;
    }
    else if (cam_name === "d9"){
        // Hacky way to remove `b''` from bytes (when serving via python3)
        var teststring = arrayBuffer.substring(0, 2);
        if (teststring === "b'"){
            d9img.src = "data:image/jpeg;base64," + arrayBuffer.slice(2,-1);
        }
        else{
            d9img.src = "data:image/jpeg;base64," + arrayBuffer;
        }
        d9img.style.height = img_height;
        d9img.style.width = img_width;
        d9img.style.margin = "0 auto";

        optional_d9_text.innerHTML =
            "File name: ".bold().fontsize(3) + info + "</br>" +
            "Last updated: ".bold().fontsize(3) + updatetime ;
    }
    // Remove pre_panel elements
    pre_panel_text.outerHTML = " </br> ";

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
