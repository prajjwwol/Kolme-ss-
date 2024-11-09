let requirements = [];
let currentRequirementIndex = 0;
let responses = {};
let clarificationIndex = 0;

// Trigger the initial prioritization process
async function submitRequirements() {
    requirements = document.getElementById("requirements").value.split("\n").filter(Boolean);
    currentRequirementIndex = 0;
    responses = {};
    askNextQuestion();
}

// Display the next question for each requirement
function askNextQuestion() {
    if (currentRequirementIndex < requirements.length) {
        const requirement = requirements[currentRequirementIndex];
        document.getElementById("modal-question").innerText = `Question for: ${requirement}`;
        document.getElementById("importance").value = "";
        document.getElementById("complexity").value = "";
        document.getElementById("urgency").value = "";
        openModal();
    } else {
        finalizePrioritization();
    }
}

// Open the modal overlay for input
function openModal() {
    document.getElementById("modal-overlay").classList.add("show");
    document.getElementById("question-modal").classList.add("show");
}

// Close the modal overlay
function closeModal() {
    document.getElementById("modal-overlay").classList.remove("show");
    document.getElementById("question-modal").classList.remove("show");
}

// Submit the answer for the current question
function submitAnswer() {
    const importance = document.getElementById("importance").value || 3;
    const complexity = document.getElementById("complexity").value || 3;
    const urgency = document.getElementById("urgency").value || 3;

    responses[requirements[currentRequirementIndex]] = {
        importance: parseInt(importance, 10),
        complexity: parseInt(complexity, 10),
        urgency: parseInt(urgency, 10),
    };

    currentRequirementIndex++;
    closeModal();
    askNextQuestion();
}

// Finalize prioritization and send data to backend
async function finalizePrioritization() {
    const response = await fetch('/prioritize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ requirements, responses })
    });

    if (response.ok) {
        const result = await response.json();
        displayResults(result);
    } else {
        console.error("Error in prioritization process.");
    }
}

// Display the prioritization results and handle any information requests
function displayResults(result) {
    let output = "<h3>Prioritized Requirements:</h3><ul>";
    result.prioritized.forEach(({ requirement, score, explanation }) => {
        output += `<li class="result-item"><strong>${requirement}</strong> - Score: ${score.toFixed(2)}<br>${explanation}</li>`;
    });
    output += "</ul>";

    document.getElementById("results").innerHTML = output;

    //  additional clarification requests check
    if (result.information_requests && result.information_requests.length > 0) {
        clarificationIndex = 0;
        displayClarificationRequests(result.information_requests);
    } else {
        document.getElementById("additional-info").innerHTML = "";
    }
}

// Display clarification requests
function displayClarificationRequests(informationRequests) {
    let clarificationOutput = "<h3>Additional Information Needed:</h3><ul>";
    informationRequests.forEach((request, index) => {
        clarificationOutput += `
            <li class="clarification-item">${request}<br>
            <input type="text" id="clarification${index}" placeholder="Provide clarification">
            <button onclick="submitClarification(${index}, '${requirements[index]}')">Submit Clarification</button>
            </li>
        `;
    });
    clarificationOutput += "</ul>";
    document.getElementById("additional-info").innerHTML = clarificationOutput;
}

// Handle additional clarification submissions
async function submitClarification(index, requirement) {
    const clarification = document.getElementById(`clarification${index}`).value;
    responses[requirement] = { ...responses[requirement], clarification };

    const response = await fetch('/prioritize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ requirements, responses })
    });

    if (response.ok) {
        const result = await response.json();
        displayResults(result); //updated clarifications
        document.getElementById(`clarification${index}`).value = '';
    } else {
        console.error("Error submitting clarification.");
    }
}
