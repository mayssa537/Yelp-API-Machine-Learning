var geojson_final = []

for (i = 0; i < names.length; i++) {
	var geojson = {
		"type": "Feature",
		"properties": {
			"names": '',
			"categories": '',
			"ratings": '',
			"price": '',
			"address": '',
			"city": '',
			"zipCode": '',
			"state": '',
			"show_on_map": true
		},
		"geometry": {
			"type": "Point",
			"coordinates": []
		}
	};

	geojson.properties.names = names[i];
	geojson.properties.categories = categories[i];
	geojson.properties.ratings = ratings[i];
	geojson.properties.price = price[i];
	geojson.properties.address = address[i];
	geojson.properties.city = city[i];
	geojson.properties.zipCode = zipCode[i];
	geojson.properties.state = state[i];
	geojson.geometry.coordinates = [latitude[i], longitude[i]];

	geojson_final.push(geojson)
}
console.log(geojson_final)

var myMap = L.map("map", {
	center: geojson_final[0].geometry.coordinates,
	zoom: 11
});

// Adding a tile layer (the background map image) to our map
// We use the addTo method to add objects to our map
L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
	attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
	maxZoom: 18,
	id: "mapbox.streets",
	accessToken: "pk.eyJ1Ijoic21vcnRlemF2aSIsImEiOiJjangweXg2dHAwMjR2NDRuenZobjFuOG9jIn0.jiVwTVGuAEaYH-mTB9t7xA"
}).addTo(myMap);

d3.json(geojson_final, function (data) {
	// Once we get a response, send the data.features object to the createFeatures function
	createFeatures(data);
});

function createFeatures(earthquakeData) {

	// Define a function we want to run once for each feature in the features array
	// Give each feature a popup describing the place and time of the earthquake
	function onEachFeature(feature, layer) {
		layer.bindPopup("<h3>" + feature.properties.ratings +
			"</h3><hr><p>" + new Date(feature.properties.names) + "</p>");
	}

	for (var i = 0; i < geojson_final.length; i++) {
		var restaurant = geojson_final[i];
		L.marker(restaurant.geometry.coordinates)
			.bindPopup("<h5>" + restaurant.properties.names + "</h5><hr><p>" + " " + "Address: " + restaurant.properties.address + ", " + restaurant.properties.city + ", " + restaurant.properties.zipCode + "<br>" + "Rating: " + restaurant.properties.ratings + "<br>" + "Price: " + restaurant.properties.price + "</p>")
			.addTo(myMap);
	}
}