document.addEventListener("DOMContentLoaded", () => {
    let requirements = [];
    let currentRequirementIndex = 0;
    let responses = {};

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
            const modalQuestion = document.getElementById("modal-question");
            const importanceInput = document.getElementById("importance");
            const complexityInput = document.getElementById("complexity");
            const urgencyInput = document.getElementById("urgency");

            if (modalQuestion && importanceInput && complexityInput && urgencyInput) {
                modalQuestion.innerText = `Question for: ${requirement}`;
                importanceInput.value = "";
                complexityInput.value = "";
                urgencyInput.value = "";
                openModal();
            } else {
                console.error("Modal elements not found.");
            }
        } else {
            finalizePrioritization();
        }
    }

    // Open the modal overlay for input
    function openModal() {
        const modalOverlay = document.getElementById("modal-overlay");
        const questionModal = document.getElementById("question-modal");

        if (modalOverlay && questionModal) {
            modalOverlay.classList.add("show");
            questionModal.classList.add("show");
        } else {
            console.error("Modal overlay elements not found.");
        }
    }

    // Close the modal overlay
    function closeModal() {
        const modalOverlay = document.getElementById("modal-overlay");
        const questionModal = document.getElementById("question-modal");

        if (modalOverlay && questionModal) {
            modalOverlay.classList.remove("show");
            questionModal.classList.remove("show");
        } else {
            console.error("Modal overlay elements not found.");
        }
    }

    // Submit the answer for the current question
    function submitAnswer() {
        const importance = document.getElementById("importance")?.value || 3;
        const complexity = document.getElementById("complexity")?.value || 3;
        const urgency = document.getElementById("urgency")?.value || 3;

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

    // Displays the prioritization results
    function displayResults(result) {
        let output = "<h3>Prioritized Requirements:</h3><ul>";

        result.prioritized.forEach(({ requirement, score, explanation }) => {
            output += `<li class="result-item"><strong>${requirement}</strong> - Score: ${score.toFixed(2)}<br>${explanation}</li>`;
        });
        output += "</ul>";

        const resultsContainer = document.getElementById("results");
        if (resultsContainer) {
            resultsContainer.innerHTML = output;
        } else {
            console.error("Results container not found.");
        }

        // Clear any remaining clarification requests after submission
        const additionalInfoContainer = document.getElementById("additional-info");
        if (additionalInfoContainer) {
            additionalInfoContainer.innerHTML = "";
        } else {
            console.error("Additional info container not found.");
        }
    }

    // Displays clarification requests
    function displayClarificationRequests(informationRequests) {
        let clarificationOutput = "<h3>Additional Information Needed:</h3><ul>";
        informationRequests.forEach((request, index) => {
            clarificationOutput += `
                <li class="clarification-item">
                    ${request}<br>
                    <input type="text" id="clarification${index}" placeholder="Provide clarification">
                </li>
            `;
        });
        clarificationOutput += `</ul>
            <button onclick="submitAllClarifications(${informationRequests.length})">Submit All Clarifications</button>`;

        const additionalInfoContainer = document.getElementById("additional-info");
        if (additionalInfoContainer) {
            additionalInfoContainer.innerHTML = clarificationOutput;
        } else {
            console.error("Additional info container not found.");
        }
    }

    // Handles additional clarification submissions
    async function submitAllClarifications(totalRequests) {
        for (let i = 0; i < totalRequests; i++) {
            const clarificationInput = document.getElementById(`clarification${i}`);
            const clarificationText = clarificationInput?.value || "";
            
            const requirementText = clarificationInput.closest('li').innerText.split("\n")[0];
            responses[requirementText] = { ...responses[requirementText], clarification: clarificationText };
        }

        const response = await fetch('/prioritize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ requirements, responses })
        });

        if (response.ok) {
            const result = await response.json();
            displayResults(result);
            const additionalInfoContainer = document.getElementById("additional-info");
            if (additionalInfoContainer) {
                additionalInfoContainer.innerHTML = "";
            }
        } else {
            console.error("Error submitting clarifications.");
        }
    }

    // Expose functions to global scope if needed
    window.submitRequirements = submitRequirements;
    window.submitAnswer = submitAnswer;
});
