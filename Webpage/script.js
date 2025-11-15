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
	var gripBtn = document.getElementById("grip-btn");
	var undoBtn = document.getElementById("undo-btn");
	snapshotBtn.addEventListener("click", takeSnapshot);
	pauseBtn.addEventListener("click", addPause);
	gripBtn.addEventListener("click", changeGrip);
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
	if(list.lastChild){
		list.removeChild(list.lastChild);
	}
}

function addPause() {

}

function takeSnapshot() {

}

function changeGrip() {
	
}