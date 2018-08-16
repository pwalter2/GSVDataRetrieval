/*
* Author: Paul Walter (pwalter2@stanford.edu)
* Description: Scrapes Google Street View to obtain visual data for
* processing and analysis. A sub-project of the Grid Resilience and
* Intelligence Platform (GRIP) created by the GISMo Group
* (http://gismo.slac.stanford.edu/projects/grip.html)
*/

//INCREMENT must be small enough s.t. no pan_id's are missed
const INCREMENT = 0.0001; //chosen via trial and error
const URL_BASE_META = "https://maps.googleapis.com/maps/api/streetview/metadata?";

function getUserInput() {
    let start = prompt("Input coordinates of the northwest corner.\n" +
                        "FORMAT: LATITUDE, LONGITUDE", "37.43526, -67.43312");
    let end = prompt("Input coordinates of the southwest corner\n" +
                      "FORMAT: LATITUDE, LONGITUDE", "37.43526, -67.43312");
    let key = prompt("Insert Google API key with usage and billing enabled.");
    if (start != null && end != null && key != null) {
        start = start.split(",");
        start[0] = Number(start[0]);
        start[1] = Number(start[1]);
        end = end.split(",");
        end[0] = Number(end[0]);
        end[1] = Number(end[1]);
        let numRequests = (Math.floor(Math.abs(end[0] - start[0]) / INCREMENT) + 1)
                        * (Math.floor(Math.abs(end[1] - start[1]) / INCREMENT) + 1);
        alert("The given input will create " + numRequests +
                " HTTP requests.\n" + "Expected load time is at least:\n" +
                getLoadTime(numRequests)
             );
        scrapeGSV(start, end, key);
    }
}

function getLoadTime(numRequests) {
    //assuming 10 HTTP requests per second
    let totSecs = numRequests / 10;
    let hours = Math.floor(totSecs / 3600);
    totSecs %= 3600;
    let mins = Math.floor(totSecs / 60);
    let secs = totSecs % 60;
    return `${hours} hours, ${mins} mins, ${secs} secs`;
}

function scrapeGSV(start, end, key) {
    let seenIDs = new Set();
    let numRequests = (Math.floor(Math.abs(end[0] - start[0]) / INCREMENT) + 1)
                    * (Math.floor(Math.abs(end[1] - start[1]) / INCREMENT) + 1);
    let errorObj = {
        "notGoogle" : 0,
        "tooOld" : 0,
        "repeat" : 0,
        "noResult" : 0
    };
    //NORTH,EAST : positive Lat/Lng |SOUTH, WEST: negative Lat/Lng
    for (let thisLat = start[0]; thisLat >= end[0]; thisLat -= INCREMENT) {
        for (let thisLng = start[1]; thisLng <= end[1]; thisLng += INCREMENT) {
            let http = new XMLHttpRequest();
            let coord = thisLat.toString() + "," + thisLng.toString();
            http.open('GET', URL_BASE_META + "location=" + coord
                        + "&key=" + key, false);
            http.send();
            let response = JSON.parse(http.responseText);
            switch (responseType(response, seenIDs)) {
                case 0:
                    errorObj.noResult++;
                    break;
                case 1:
                    errorObj.repeat++;
                    break;
                case 2:
                    errorObj.notGoogle++;
                    break;
                case 3:
                    errorObj.tooOld++;
                    break;
                case 4:
                    document.getElementById("output").innerHTML +=
                    response.pano_id + ",<br>";
                    seenIDs.add(response.pano_id);
            }
        }
    }
    finalReport(numRequests, errorObj);
}

function finalReport(numRequests, errorObj) {
    let zeroResultsP = errorObj.noResult / numRequests;
    let repeatP = errorObj.repeat / (numRequests - errorObj.noResult);
    let nonGoogP = errorObj.notGoogle /
                    (numRequests - errorObj.noResult - errorObj.repeat);
    let tooOldP = errorObj.tooOld /
                    (numRequests - errorObj.noResult - errorObj.repeat -
                    errorObj.notGoogle);
    alert("Program Complete: Valid Panorama IDs listed below.\n" +
           "Error Reporting:\n" +
           "Number of Requests: " + numRequests + "\n" +
           "No Results: " + zeroResultsP + "\n" +
            "Repeated Query: " + repeatP + "\n" +
            "Non-Google Conent: " + nonGoogP + "\n" +
            "Picture older than a year: " + tooOldP + "\n" +
            "Note: Each percentage is conditional probability given " +
            "that the query made it to that stage of the filtration process. " +
            "Order of filtration is as given. Furthermore, a small number of " +
            "repeated queries is good to ensure that all panoramas are visited."
        );
        //Do the python and...
        //-ESTMIATED COST TO DOWNLOAD/RETRIEVE ALL PICTURES
        //-ESTIMATED STORAGE TO DOWNLOAD ALL PICTURES
}


// Determines how old a date is from today.
//date is a string in format YYYY-MM
//returns the difference in months
function dateDifference(date) {
    let now = new Date();
    let year = Number(date.substring(0,4));
    let month = Number(date.substring(5));
    return (now.getFullYear() - year) * 12 + now.getMonth() -
                        (month - 1);
}



//error checking for HTML requests
function responseType(response, seenIDs) {
    if (response.status !== "OK") return 0; //no results
    if (seenIDs.has(response.pano_id)) return 1; //repeat
    if (response.copyright !== "© Google, Inc.") return 2; //non-google
    if (dateDifference(response.date) >= 12) return 3; //older than a year
    return 4;
}
