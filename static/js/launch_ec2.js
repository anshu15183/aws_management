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

	const spinner = document.getElementById("spinner");
	const overlay = document.getElementById("overlay");
	const launchForm = document.getElementById("launchForm");
	const regionSelect = document.getElementById("region");
	const instanceTypeSelect = document.getElementById("instance_type");
	const amiIdSelect = document.getElementById("ami_id");

	// Hide the spinner and overlay initially
	spinner.style.display = "none";
	overlay.style.display = "none";

	// Handle form submission via AJAX
	launchForm.addEventListener("submit", function (event) {
		event.preventDefault(); // Prevent the default form submission

		// Show the spinner and overlay
		spinner.style.display = "block";
		overlay.style.display = "block";

		var formData = new FormData(this);

		// Send AJAX request to launch EC2 instance
		fetch("/launch_ec2", {
			method: "POST",
			body: formData,
		})
			.then((response) => response.json())
			.then((data) => {
				// Hide the spinner and overlay
				spinner.style.display = "none";
				overlay.style.display = "none";

				// Display the message from the backend
				if (data.message) {
					document.getElementById("message").textContent = data.message;
				}
				// Clear the form fields
				launchForm.reset();
			})
			.catch((error) => {
                // Hide the spinner and overlay in case of an error
				spinner.style.display = "none";
				overlay.style.display = "none";
				console.error("Error:", error);
                launchForm.reset();
			});
	});

	// Fetch AMIs based on selected region when region changes
	regionSelect.addEventListener("change", function () {
		// Show the spinner and overlay
		spinner.style.display = "block";
		overlay.style.display = "block";
		const selectedRegion = regionSelect.value.trim();

		if (!selectedRegion) {
			alert("Please select a region.");
			return;
		}

		console.log("Fetching AMIs for region:", selectedRegion); // Debug log

		// Prepare form data
		const formData = new FormData();
		formData.append("region", selectedRegion);

		fetch("/get_amis", {
			method: "POST",
			body: formData,
		})
			.then((response) => {
				if (!response.ok) {
					throw new Error("Network response was not ok");
				}
				return response.json();
			})
			.then((data) => {
				// Hide the spinner and overlay
				spinner.style.display = "none";
				overlay.style.display = "none";
				if (data.error) {
					console.error("Server error:", data.error);
					return;
				}
				console.log("AMIs received:", data.amis); // Debug log

				// Clear existing AMI IDs
				amiIdSelect.innerHTML = '<option value="" disabled selected>Select an AMI ID</option>';

				// Add new AMI IDs
				data.amis.forEach((ami) => {
					const option = document.createElement("option");
					option.value = ami.ami_id;
					option.textContent = `${ami.ami_id} (${ami.os})`;
					amiIdSelect.appendChild(option);
				});
			})
			.catch((error) => {
				console.error("Error fetching AMIs:", error);
				// Hide the spinner and overlay in case of an error
				spinner.style.display = "none";
				overlay.style.display = "none";
			});
	});
});
