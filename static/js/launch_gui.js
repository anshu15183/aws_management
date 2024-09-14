document.addEventListener("DOMContentLoaded", function () {
	// Prevent default button actions that may cause reloads
	const buttons = document.querySelectorAll("button");
	buttons.forEach((button) => {
		button.addEventListener("click", function (event) {
			if (button.dataset.reload === "true") {
				event.preventDefault();
				promptReloadConfirmation();
			}
		});
	});

	// Confirm before page reload
	window.addEventListener("beforeunload", function (event) {
		const confirmationMessage = "Are you sure you want to leave this page? Unsaved changes may be lost.";
		event.returnValue = confirmationMessage;
		return confirmationMessage;
	});

	// Function to prompt user before reloading
	function promptReloadConfirmation() {
		if (confirm("Do you really want to reload the page? Unsaved changes will be lost.")) {
			location.reload();
		} else {
			console.log("Page reload canceled.");
		}
	}

	// Get key elements
	const spinner = document.getElementById("spinner");
	const overlay = document.getElementById("overlay");
	const launchForm = document.getElementById("launchGuiForm");
	const messageBox = document.getElementById("message");

	// Hide spinner and overlay initially
	spinner.style.display = "none";
	overlay.style.display = "none";

	// Handle the form submission for launching the RHEL GUI

	launchForm.addEventListener("submit", function (event) {
		event.preventDefault();

		// Show spinner and overlay
		spinner.style.display = "block";
		overlay.style.display = "block";

		var formData = new FormData(this);

		fetch("/launch_gui_rhel", {
			method: "POST",
			body: formData,
		})
			.then(async (response) => {
				if (!response.ok) {
					const errorData = await response.json();
					throw new Error(errorData.message || "An unexpected error occurred.");
				}
				return response.json();
			})
			.then((data) => {
				if (spinner) spinner.style.display = "none";
				if (overlay) overlay.style.display = "none";

				if (data && data.message) {
					alert(data.message);
					if (messageBox) messageBox.innerText = data.message;
				}

				launchForm.reset();
			})
			.catch((error) => {
				if (spinner) spinner.style.display = "none";
				if (overlay) overlay.style.display = "none";
				console.error("Error:", error);
				alert(`Error: ${error.message}`);
				launchForm.reset();
			});
	});
});
