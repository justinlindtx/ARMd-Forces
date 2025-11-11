var selectedMode;

function main() {
	selectedMode = localStorage.getItem("mode") || "coord";
	var selectElement = document.getElementById("select");
	selectElement.addEventListener("change", modeChange);
	selectElement.value = selectedMode;
	let event = new Event('change');
    selectElement.dispatchEvent(event);
}

function modeChange() {
	selectedMode = this.value;
	localStorage.setItem("mode", selectedMode);
	var modes = document.getElementsByClassName("mode");
	var selMode = document.getElementById(this.value);
	for (let i = 0; i < modes.length; i++) {
		modes[i].style.display = "none";
	}
	selMode.style.display = "block";
}
