//
// Script to grab the image, encode it and return
//

var pre_panel_text = document.getElementById("pre_panel_text");
var post_panel_text = document.getElementById("post_panel_text");
var d6img = document.getElementById("AudubonCamD6");
var d9img = document.getElementById("AudubonCamD9");
var optional_d6_text = document.getElementById("optional_d6_text");
var optional_d9_text = document.getElementById("optional_d9_text");
var message_received_once = false;
var arrayBuffer;
var img_height = '500';
var img_width = '500';
var $message = $("#message");
var $d6_tl = $("#d6_timelapse");
var $d9_tl = $("#d9_timelapse");
// Hide timelapse video at first
$d6_tl.hide();
$d9_tl.hide();

// If site is accessed when cams are not live
var hour_now = new Date().getHours();
if (hour_now >= 8 && hour_now <=21){
    $message.attr("class", 'badge badge-pill badge-danger');
    $message.text('Not Live');
    var pre_message = "Cameras are Not live Now</br>"
    pre_message = pre_message.fontsize("4").fontcolor("#000000");
    pre_panel_text.innerHTML = pre_message;
    pre_panel_text.style.textAlign="center";
    $d6_tl.show();
    $d9_tl.show();
    var post_message = "Cameras are generally live between 9pm and 6am"
    post_message = post_message.fontsize("3").fontcolor("#D3D3D3").bold();
    post_panel_text.innerHTML = post_message;
    post_panel_text.style.textAlign="center";
}
else {
    
    //var ws = new WebSocket("ws://localhost:8888/realtime");
    var ws = new WebSocket("wss://dashsense.cusp.nyu.edu/realtime");
    ws.binaryType = 'arraybuffer';
    
    ws.onopen = function(){
        $message.attr("class", 'badge badge-pill badge-info');
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
	        $message.attr("class", 'badge badge-pill badge-warning');
	        $message.text('Error');
	        var pre_message = "Connecting to the Live Feed is taking longer than usual.</br>" +
                    "While I try to connect, here are the timelapse videos from previous night";
	        pre_message = pre_message.fontsize("4").fontcolor("#000000").bold();
	        pre_panel_text.innerHTML = pre_message;
	        pre_panel_text.style.textAlign="center";
                // Remind the timings when feed is live
                var post_message = "Cameras are generally live between 9pm and 6am";
                post_message = post_message.fontsize("3").fontcolor("#D3D3D3").bold();
                post_panel_text.innerHTML = post_message;
                post_panel_text.style.textAlign="center";
                // If No Live feed, Play time lapse video
                $d6_tl.show();
                $d9_tl.show();
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
        $message.attr("class", 'badge badge-pill badge-success');
        $message.text("Live");
        // hide the timelapse if it was playing
        $d6_tl.hide();
        $d9_tl.hide();
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
            optional_d6_text.innerHTML = "Last updated: ".bold().fontsize(3) + updatetime ;
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
            
            optional_d9_text.innerHTML = "Last updated: ".bold().fontsize(3) + updatetime ;
        }
        // Remove pre_panel elements
        pre_panel_text.outerHTML = " </br> ";
        
    };
    
    ws.onclose = function(ev){
        $d6_tl.show();
        $d9_tl.show();
        $message.attr("class", 'badge badge-pill badge-danger');
        $message.text('Not Live');
        console.log("connection was closed");
    };
    
    ws.onerror = function(ev){
        $message.attr("class", 'badge badge-pill badge-secondary');
        $message.text('Error');
        var message = "Could not connect to the Live Feed. <br/> Contact mohit.sharma@nyu.edu";
        message = message.fontsize("4").fontcolor("#000000").bold();
        optional_text.innerHTML = message;
        optional_text.style.textAlign="center";
        console.log("Error in establishing connection");
        $d6_tl.show();
        $d9_tl.show();
    };
}
