// JavaScript file for handling the state of the html webpage

var selectedMode;
var lastGripState = null;
var lastSnapshotGripState = null;
var snapshotMade = false;
var rawCoordValues = [];

// Find initial grip state
(async () => {
	const r = await fetch("/grip-state");
	lastGripState = await r.text();  // "open" or "close"
})();

function main() {
	// Set up mode selection
	selectedMode = localStorage.getItem("mode") || "coord"; // Gets previously selected mode if exists, or "coord" by default
	var selectElement = document.getElementById("select");
	selectElement.addEventListener("change", modeChange);
	selectElement.value = selectedMode;
    selectElement.dispatchEvent( new Event('change') );
	
	// Disable the display of control panel
	document.getElementById("control-panel-box").style.display = "none";
	
	// Getting buttons from html
	var gripBtn = document.getElementById("gripper");
	var snapshotBtn = document.getElementById("snapshot-btn");
	var pauseBtn = document.getElementById("pause-btn");
	var pauseSubmit = document.getElementById("submit-pause");
	var undoBtn = document.getElementById("undo-btn");
	var saveBtn = document.getElementById("save-btn");
	var sendRoutineBtn = document.getElementById("submit-routine");
	var runRoutineBtn = document.getElementById("run");
	gripBtn.addEventListener("click", toggleGrip);
	snapshotBtn.addEventListener("click", takeSnapshot);
	pauseBtn.addEventListener("click", showPauseForm);
	pauseSubmit.addEventListener("click", addPause);
	undoBtn.addEventListener("click", undoAction);
	saveBtn.addEventListener("click", showSaveForm);
	sendRoutineBtn.addEventListener("click", sendRoutine);
	runRoutineBtn.addEventListener("click", runRoutine);
}

// Called every time mode changes
function modeChange() {
	// Gets selected mode
	selectedMode = this.value;
	localStorage.setItem("mode", selectedMode);
	
	// Sends mode to server
	fetch("/change-mode", {   // same server
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: selectedMode })
    })
	
	// Makes control panel visible if mode is "manual" or "create"
	var controlPanel = document.getElementById("control-panel");
	if(selectedMode === "manual"){
		var placeholder = document.getElementById("manual-control-placeholder");
		placeholder.appendChild(controlPanel);
	}
	else if(selectedMode === "create"){
		var placeholder = document.getElementById("control-placeholder");
		placeholder.appendChild(controlPanel);
	}
	
	// Makes coresponding elements for the mode visible/invisible
	var modes = document.getElementsByClassName("mode");
	var selMode = document.getElementById(this.value);
	for (let i = 0; i < modes.length; i++) { // Hides all mode elements
		modes[i].style.display = "none";
	}
	selMode.style.display = "block"; // Shows selected mode elements

	if(selectedMode == "run-routine"){
		loadRoutines();
	}
}

// Removes the most recently added action element
function undoAction() {
	document.getElementById("pause-submission-form").style.display = "none";
	var list = document.getElementById("list");
	if(list.lastElementChild){
		list.removeChild(list.lastElementChild);
	}
}

// Shows the pause form
function showPauseForm() {
	document.getElementById("pause-submission-form").style.display = "block";
	document.getElementById("routine-submission-form").style.display = "none";
}

// Adds a pause as an element and displays it.
function addPause() {
	document.getElementById("pause-submission-form").style.display = "none";
	var entry = document.getElementById("pause-duration");
	var duration = parseFloat(entry.value);
	entry.value = "";
	if(isNaN(duration)){
		console.log("Invalid input");
		return;
	}
	var list = document.getElementById("list");
	var newpause = document.createElement("li");
	newpause.textContent = "Pause: " + duration + " sec";
	list.appendChild(newpause);
	newpause.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// Gets the current servo positions from the servo, creates an element and displays it.
async function takeSnapshot() {
	document.getElementById("pause-submission-form").style.display = "none";
	try {
		var response = await fetch("/get-coords"); // get coords from the server
		var data = await response.json();
		var snapshotID = crypto.randomUUID();
		rawCoordValues.push({id: snapshotID, raw: data}); // store full values
		var formatted = data.map(n => Number(n).toFixed(2)).join(", "); // display rounded values

		var list = document.getElementById("list");

		if(!snapshotMade){ // first snapshot always includes a grip entry
			var gripSnapshot = document.createElement("li");
			gripSnapshot.textContent = "Grip: " + lastGripState;
			list.appendChild(gripSnapshot);
			gripSnapshot.scrollIntoView({ behavior: "smooth", block: "nearest" });
			snapshotMade = true;
		}
		else if(lastGripState != lastSnapshotGripState){ // if grip changed since last snapshot
			var gripSnapshot = document.createElement("li");
			gripSnapshot.textContent = "Grip: " + lastGripState;
			list.appendChild(gripSnapshot);
			gripSnapshot.scrollIntoView({ behavior: "smooth", block: "nearest" });
		}

		lastSnapshotGripState = lastGripState;
		
		var snapshot = document.createElement("li");
		snapshot.dataset.rawid = snapshotID;
		snapshot.textContent = "Move: " + formatted;
		list.appendChild(snapshot);
		snapshot.scrollIntoView({ behavior: "smooth", block: "nearest" });

	} catch (err) {
		console.error(err.message);
	}
}

// Shows the save submission form for routine creation
function showSaveForm() {
	document.getElementById("routine-submission-form").style.display = "block";
	document.getElementById("pause-submission-form").style.display = "none";
}

// Sends the current routine as a JSON file to be saved by the server
async function sendRoutine() {
	document.getElementById("routine-submission-form").style.display = "none";
	var name = document.getElementById("routine-name");
	var routineName = name.value;
	name.value = "";
	var routineItems = document.querySelectorAll("#list li");
	var payload = [];
	payload.push({name: routineName});
	routineItems.forEach(li => {
		var text = li.textContent;
		if(text.startsWith("Move: ")){
			var id = li.dataset.rawid;
			var entry = rawCoordValues.find(x => x.id == id);
			payload.push({type: "move", coords: entry.raw}); // send unrounded values
		}
		else if(text.startsWith("Pause: ")){
			payload.push({type: "pause", duration: parseFloat(text.split(":")[1].replace("sec", "").trim())});
		}
		else if(text.startsWith("Grip: ")){
			payload.push({type: "grip", state: text.slice(6)});
		}
	});
	
	await fetch("/submit-routine", {
		method: "post",
		headers: {"Content-Type": "application/json"},
		body: JSON.stringify(payload)
	});

	// Clears the list
	var list = document.getElementById("list");
	list.replaceChildren();
}

// Loads and displays locally stored JSON routines by requesting them from the server
async function loadRoutines() {
	var response = await fetch("/list-files");
	var files = await response.json();
	var select = document.getElementById("routineSelect");
	select.innerHTML = ""; // Clears old options

	var blank = document.createElement("option");
	blank.value = "";
	blank.textContent = "";
	select.append(blank);

	for(var file of files){
		var option = document.createElement("option");
		option.value = file;
		option.textContent = file;
		select.append(option);
	}
}

// Sends the server the selected routine's JSON file
async function runRoutine() {
	var selectedRoutine = document.getElementById("routineSelect");
	if(selectedRoutine.value == "") return;

	await fetch("/run-routine", {
		method: "post",
		headers: {"Content-Type": "application/json"},
		body: JSON.stringify(selectedRoutine.value)
	});
}

// Sends the server a request to toggle grip
async function toggleGrip() {
	var response = await fetch("/grip");
	var newState = await response.text();
	lastGripState = newState;
}