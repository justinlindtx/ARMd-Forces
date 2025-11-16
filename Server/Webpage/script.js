var selectedMode;

function main() {
	selectedMode = localStorage.getItem("mode") || "coord";
	var selectElement = document.getElementById("select");
	selectElement.addEventListener("change", modeChange);
	selectElement.value = selectedMode;
	let event = new Event('change');
    selectElement.dispatchEvent(event);

	var snapshotBtn = document.getElementById("snapshot-btn");
	var pauseBtn = document.getElementById("pause-btn");
	var pauseSubmit = document.getElementById("submit-pause");
	var undoBtn = document.getElementById("undo-btn");
	snapshotBtn.addEventListener("click", takeSnapshot);
	pauseBtn.addEventListener("click", showPauseForm);
	pauseSubmit.addEventListener("click", addPause);
	undoBtn.addEventListener("click", undoAction);
}

function modeChange() {
	selectedMode = this.value;
	localStorage.setItem("mode", selectedMode);
	var modes = document.getElementsByClassName("mode");
	var selMode = document.getElementById(this.value);
	for (let i = 0; i < modes.length; i++) { // hide all modes
		modes[i].style.display = "none";
	}
	selMode.style.display = "block"; // show selected mode

	var controlPanel = document.getElementById("control-panel");
	if(selectedMode == "manual"){
		var placeholder = document.getElementById("manual-control-placeholder");
		placeholder.appendChild(controlPanel);
	}
	else if(selectedMode == "create"){
		var placeholder = document.getElementById("control-placeholder");
		placeholder.appendChild(controlPanel);
	}
}

function undoAction() {
	var list = document.getElementById("list");
	if(list.lastElementChild){
		list.removeChild(list.lastElementChild);
	}
}

function showPauseForm() {
	document.getElementById("pause-submission-form").style.display = "block";
}

function addPause() {
	var duration = parseFloat(document.getElementById("pause-duration").value);
	if(isNaN(duration)){
		console.log("Invalid input");
		return;
	}
	var list = document.getElementById("list");
	var newpause = document.createElement("li");
	newpause.textContent = "Pause: " + duration + " sec";
	list.appendChild(newpause);

	document.getElementById("pause-submission-form").style.display = "none";
}

async function takeSnapshot() {
	try {
		var response = await fetch("/get-coords"); // get coords from the server
		var data = await response.json();
		var formatted = data.map(n => Number(n).toFixed(2)).join(", ");

		var list = document.getElementById("list");
		var snapshot = document.createElement("li");
		snapshot.textContent = "Move: " + formatted;
		list.appendChild(snapshot);

	} catch (err) {
		console.error(err.message);
	}
}