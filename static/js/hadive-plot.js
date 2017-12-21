// Create map
// Extract the width and height that was computed by CSS
var plotDiv = document.getElementById("plot");
var width = plotDiv.clientWidth;
var height = plotDiv.clientHeight;
var padding = 20;
var margin = {top: 60, right: 30, bottom: 80, left: 70};
var svg = d3.select(plotDiv)
    .classed("svg-container", true) //container class to make it responsive
    .append("svg")
    .attr("preserveAspectRatio", "xMinYMin meet") //responsive SVG needs these 2 attributes and no width and height attr
    .attr("viewBox", "0 0 1200 800")
    .classed("svg-content-responsive", true); //class to make it responsive

var x = d3.time.scale().range([0, width]);
var y = d3.scale.linear().range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom").ticks(5);

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left"); //.ticks(10);

var valueline = d3.svg.line()
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.count); });


var map = L.map("map", {center: [40.72, -73.95], zoom: 10});

L.tileLayer("http://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://cartodb.com/attributi\
\
ons">CartoDB</a>'
}).addTo(map);

// Load geojson.
$.getJSON("/static/data/cameras.json", function(data) { addDataToMap(data, map); });

// Add data to map.
function addDataToMap(data, map) {
    var dataLayer = L.geoJson(data, {
        onEachFeature: camdesc
    });
    dataLayer.addTo(map);
}
// Function on-click
function camdesc(feature, layer) {
    //bind click
    layer.on('click', function (event) {
        document.getElementById("map_placeholder").innerHTML=''
        document.getElementById("cam").innerHTML = "<img src='/static/imgs/collected_ims/" + feature.properties.name + ".jpg' style='max-width\
:100%'></img>";
        document.getElementById("desc").innerHTML = "<p class='lead'>" + feature.properties.description + "</h3>";
        document.getElementById("desc").innerHTML += "<p>Camera ID: " + feature.properties.name + "</p>";
        document.getElementById("desc").innerHTML += "<p>Latitude: " + feature.geometry.coordinates[1] + "</p>";
        document.getElementById("desc").innerHTML += "<p>Longitude: " + feature.geometry.coordinates[0] + "</p>";
        document.getElementById("desc").innerHTML += "<p><a href='http://dotsignals.org/google_popup.php?cid=" + feature.properties.name + "'target='popup' onclick='window.open('http://dotsignals.org/google_popup.php?cid=" + feature.properties.cctv + "','DOT Camera','width=400,height=300')'>Visit the DOT Camera</a>";

        d3.csv("/static/data/weekdayavg.csv", function(data){
            data = data.filter(function(row) {
                return row['cam'] == feature.properties.name;
            })

            var parseDate = d3.time.format("%Y-%m-%d %H:%M:%S").parse;

            data.forEach(function(d) {
                d.date = parseDate(d.date); //get rid of this when you connect to the database.
                d.count = +d.count;
            });

            var bisectDate = d3.bisector(function(d) { return d.date; }).left;

            // Clear contents
            svg.selectAll("*").remove();

            x.domain(d3.extent(data, function(d) { return d.date; }));
            y.domain([0, d3.max(data, function(d) { return d.count; })]);

            // Add the valueline path.
            svg.append("path")
                .attr("class", "line")
                .attr("d", valueline(data));

            // Add the X Axis
            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

            // Add the Y Axis
            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis);

            // Add axis labels
            svg.append("text")
                .attr("text-anchor", "middle")
                .attr("transform", "translate("+ (width/2) +","+(height+(padding*1.8))+")")
                .text("Time");

            svg.append("text")
                .attr("text-anchor", "middle")
                .attr("transform", "translate("+ (-padding*2.2) +","+(height/2)+")rotate(-90)")
                .text("Pedestrian Count");

            svg.append("text")
                .attr("text-anchor", "middle")
                .attr("x", 450)
                .attr("y", -20)
                .text("Average Weekday Pedestrian Count (5 Minute Interval)")
                .style("font-size", "20px")
                .style("font-weight", "bold");

            svg.append("text")
                .attr("text-anchor", "end")
                .attr("x", 900)
                .attr("y", 255)
                .text("*Average calculated using data from 2017/06/27 to 2017/08/30.")
                .style("font-size", "10px");

            // Mouseover
            var focus = svg.append("g")
                .attr("class", "focus")
                .style("display", "none")
                .style("font-size", "14px");

            focus.append("circle")
                .attr("r", 4.5);

            svg.append("text")
                .attr("class", "datelabel")
                .attr("x", 0)
                .attr("y", 255);

            svg.append("text")
                .attr("class", "pedlabel")
                .attr("x", 0)
                .attr("y", 240);

            svg.append("rect")
                .attr("class", "overlay")
                .attr("width", width)
                .attr("height", height)
                .on("mouseover", function() { focus.style("display", null); })
                .on("mouseout", function() { focus.style("display", "none"); })
                .on("mousemove", mousemove);
            
            function mousemove() {
                var x0 = x.invert(d3.mouse(this)[0]),
                    i = bisectDate(data, x0, 1),
                    d0 = data[i - 1],
                    d1 = data[i],
                    d = x0 - d0.date > d1.date - x0 ? d1 : d0;
                focus.attr("transform", "translate(" + x(d.date) + "," + y(d.count) + ")");

                d3.select("svg")
                    .select(".datelabel")
                    .text("Time: " + d.date.getHours() + ":" + d.date.getMinutes());

                d3.select("svg")
                    .select(".pedlabel")
                    .text("Pedestrians: " + Math.round(d.count * 100) / 100);
            }
        });
    });
}
