var selectedMode;
var rawCoordValues = [];

function main() {
	selectedMode = localStorage.getItem("mode") || "coord";
	var selectElement = document.getElementById("select");
	selectElement.addEventListener("change", modeChange);
	selectElement.value = selectedMode;
	let selectEvent = new Event('change');
    selectElement.dispatchEvent(selectEvent);
	
	document.getElementById("control-panel-box").style.display = "none";

	var snapshotBtn = document.getElementById("snapshot-btn");
	var pauseBtn = document.getElementById("pause-btn");
	var pauseSubmit = document.getElementById("submit-pause");
	var undoBtn = document.getElementById("undo-btn");
	var saveBtn = document.getElementById("save-btn");
	var sendRoutineBtn = document.getElementById("submit-routine");
	snapshotBtn.addEventListener("click", takeSnapshot);
	pauseBtn.addEventListener("click", showPauseForm);
	pauseSubmit.addEventListener("click", addPause);
	undoBtn.addEventListener("click", undoAction);
	saveBtn.addEventListener("click", showSaveForm);
	sendRoutineBtn.addEventListener("click", sendRoutine);
}

function modeChange() {
	selectedMode = this.value;
	localStorage.setItem("mode", selectedMode);
	
	var controlPanel = document.getElementById("control-panel");
	if(selectedMode === "manual"){
		var placeholder = document.getElementById("manual-control-placeholder");
		placeholder.appendChild(controlPanel);
	}
	else if(selectedMode === "create"){
		var placeholder = document.getElementById("control-placeholder");
		placeholder.appendChild(controlPanel);
	}
	
	var modes = document.getElementsByClassName("mode");
	var selMode = document.getElementById(this.value);
	for (let i = 0; i < modes.length; i++) { // hide all modes
		modes[i].style.display = "none";
	}
	selMode.style.display = "block"; // show selected mode
}

function undoAction() {
	document.getElementById("pause-submission-form").style.display = "none";
	var list = document.getElementById("list");
	if(list.lastElementChild){
		list.removeChild(list.lastElementChild);
	}
}

function showPauseForm() {
	document.getElementById("pause-submission-form").style.display = "block";
	document.getElementById("routine-submission-form").style.display = "none";
}

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
}

async function takeSnapshot() {
	document.getElementById("pause-submission-form").style.display = "none";
	try {
		var response = await fetch("/get-coords"); // get coords from the server
		var data = await response.json();
		var snapshotID = crypto.randomUUID();
		rawCoordValues.push({id: snapshotID, raw: data}); // store full values
		var formatted = data.map(n => Number(n).toFixed(2)).join(", "); // display rounded values

		var list = document.getElementById("list");
		var snapshot = document.createElement("li");
		snapshot.dataset.rawid = snapshotID;
		snapshot.textContent = "Move: " + formatted;
		list.appendChild(snapshot);

	} catch (err) {
		console.error(err.message);
	}
}

function showSaveForm() {
	document.getElementById("routine-submission-form").style.display = "block";
	document.getElementById("pause-submission-form").style.display = "none";
}

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
		else {
			payload.push({type: "pause", duration: parseFloat(text.slice(7, -4))});
		}
	});
	
	await fetch("/submit-routine", {
		method: "post",
		headers: {"Content-Type": "application/json"},
		body: JSON.stringify(payload)
	});

	// Clear the list
	var list = document.getElementById("list");
	list.replaceChildren();
}