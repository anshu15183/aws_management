let lastUpdated = new Date(0); // Initial value set to epoch
let instancesData = []; // Store all instances data for filtering
let regionsWithInstances = new Set(); // Store regions with instances

// Hide spinner and overlay initially
if (spinner) spinner.style.display = "none";
if (overlay) overlay.style.display = "none";

// Function to fetch and update instance data
function fetchInstances() {
	// Show spinner and overlay
	if (spinner) spinner.style.display = "block";
	if (overlay) overlay.style.display = "block";

	fetch("/ec2/instances", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({}), // You can send data here if needed
	})
		.then((response) => {
			if (!response.ok) {
				throw new Error("Network response was not ok");
			}
			return response.json();
		})
		.then((data) => {
			if (spinner) spinner.style.display = "none";
			if (overlay) overlay.style.display = "none";
			instancesData = data; // Store data for filtering
			populateRegionFilter(data); // Populate region dropdown
			displayInstances(data); // Display all instances initially

			// Update the last updated time
			lastUpdated = new Date();
			updateTimestamp();
		})
		.catch((error) => {
			if (spinner) spinner.style.display = "none";
			if (overlay) overlay.style.display = "none";
			console.error("Error fetching instances:", error);
		});
}

// Function to populate the region filter dropdown
function populateRegionFilter(data) {
	// Clear previous options
	const regionFilter = document.getElementById("regionFilter");
	regionFilter.innerHTML = '<option value="all" selected>All Regions</option>'; // Add "All Regions" option by default

	const regions = new Set(); // Use a set to avoid duplicates

	data.forEach((instance) => {
		const region = instance["Region"]; // Fetch the region from the data
		regions.add(region); // Add each region where instances are present
	});

	// Add each unique region to the dropdown
	regions.forEach((region) => {
		const option = document.createElement("option");
		option.value = region;
		option.textContent = region;
		regionFilter.appendChild(option);
	});
}

// Function to display instances in the table
function displayInstances(data) {
	const tbody = document.querySelector("#instancesTable tbody");
	tbody.innerHTML = ""; // Clear existing rows

	data.forEach((instance) => {
		const row = document.createElement("tr");

		//const sshCommand = `ssh -i your-key.pem ec2-user@${instance["Public DNS"]}`;
		//const sshCopyButton = `<button class="copy-btn" onclick="copySSH('${sshCommand}')"><i class="fas fa-copy"></i></button>`;

		// Build the actions dropdown based on instance state
		let actionsOptions = '<option value="" disabled selected>State</option>'; // Default title
		if (instance["Instance State"] === "running") {
			actionsOptions += '<option value="stop">Stop</option>';
			actionsOptions += '<option value="reboot">Reboot</option>';
			actionsOptions += '<option value="terminate">Terminate</option>';
		} else if (instance["Instance State"] === "stopped") {
			actionsOptions += '<option value="start">Start</option>';
			actionsOptions += '<option value="reboot">Reboot</option>';
			actionsOptions += '<option value="terminate">Terminate</option>';
		} else if (instance["Instance State"] === "pending") {
			actionsOptions += '<option value="terminate">Terminate</option>';
		}

		/*row.innerHTML = `
			          <td>${instance["Name"]}</td>
			          <td>${instance["Instance ID"]}</td>
			          <td>${instance["Instance State"]}</td>
			          <td>${instance["Instance Type"]}</td>
			          <td>${instance["Availability Zone"]}</td>
			          <td>${instance["Public DNS"]}</td>
			          <td>${instance["Public IP"]}</td>
					  <td class="ssh-command">${sshCopyButton}</td>
			          <td>
			              <select class="form-control select-actions"
						  	onchange="performAction('${instance["Instance ID"]}',this.value, '${instance["Region"]}')">
			                  ${actionsOptions}
			              </select>
			          </td>
			      `;*/
		row.innerHTML = `
			          <td>${instance["Name"]}</td>
			          <td>${instance["Instance ID"]}</td>
			          <td>${instance["Instance State"]}</td>
			          <td>${instance["Instance Type"]}</td>
			          <td>${instance["Availability Zone"]}</td>
			          <td>${instance["Public DNS"]}</td>
			          <td>${instance["Public IP"]}</td>
					  
			          <td>
			              <select class="form-control select-actions"
						  	onchange="performAction('${instance["Instance ID"]}',this.value, '${instance["Region"]}')">
			                  ${actionsOptions}
			              </select>
			          </td>
			      `;

		tbody.appendChild(row);
	});
}

/*function copySSH(command) {
				navigator.clipboard.writeText(command).then(
					function () {
						alert("SSH command copied to clipboard!");
					},
					function (err) {
						console.error("Could not copy text: ", err);
					}
				);
			}*/

// Function to filter instances by region
function filterInstancesByRegion() {
	const selectedRegion = document.getElementById("regionFilter").value;

	// Filter instances based on selected region
	const filteredInstances =
		selectedRegion === "all"
			? instancesData // Show all if 'All Regions' is selected
			: instancesData.filter((instance) => instance["Region"] === selectedRegion);

	displayInstances(filteredInstances); // Update the table with filtered data
}
// Function to perform the action with confirmation
function performAction(instanceId, action, region) {
	if (action) {
		const confirmation = confirm(`Are you sure you want to ${action} this instance?`);
		if (confirmation) {
			fetch("/ec2/action", {
				method: "POST",
				headers: {
					"Content-Type": "application/x-www-form-urlencoded",
				},
				body: new URLSearchParams({
					instance_id: instanceId,
					action: action,
					region: region, // Pass the region here
				}),
			})
				.then((response) => {
					if (response.ok) {
						// Reload the table data after the action
						fetchInstances();
					} else {
						console.error("Action failed:", response.statusText);
					}
				})
				.catch((error) => console.error("Error performing action:", error));
		}
	}
}

// Function to update the timestamp
function updateTimestamp() {
	const now = new Date();
	const elapsed = Math.floor((now - lastUpdated) / 1000); // Elapsed time in seconds
	let timeString = "Just now";

	if (elapsed >= 60) {
		const minutes = Math.floor(elapsed / 60);
		timeString = `${minutes} minute${minutes > 1 ? "s" : ""} ago`;
	}

	document.getElementById("timestamp").textContent = `Last updated: ${timeString}`;
}

// Initial fetch
fetchInstances();

// Update the timestamp every minute
setInterval(updateTimestamp, 60000); // 60000 ms = 1 minute
