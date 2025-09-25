document.addEventListener("DOMContentLoaded", () => {
    const queryForm = document.getElementById("query-form");
    const companyInput = document.getElementById("company");
    const queryInput = document.getElementById("query");
    const submitButton = document.getElementById("submit-button");
    const resultContainer = document.getElementById("result-container");
    const loader = document.getElementById("loader");
    const answerOutput = document.getElementById("answer-output");

    queryForm.addEventListener("submit", async (event) => {
        event.preventDefault(); // Prevent the default form submission

        const company = companyInput.value.trim();
        const query = queryInput.value.trim();

        if (!query) {
            answerOutput.innerHTML = `<p style="color: red;">Please enter a question.</p>`;
            resultContainer.classList.remove("hidden");
            return;
        }

        // --- UI Changes for Loading State ---
        submitButton.disabled = true;
        submitButton.querySelector(".button-text").textContent = "Analyzing...";
        resultContainer.classList.remove("hidden");
        loader.style.display = "block";
        answerOutput.innerHTML = ""; // Clear previous results

        try {
            const response = await fetch("/api/query", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ company, query }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            answerOutput.textContent = data.answer;

        } catch (error) {
            console.error("Error fetching analysis:", error);
            answerOutput.innerHTML = `<p style="color: red;"><strong>An error occurred:</strong> ${error.message}</p>`;
        } finally {
            // --- Revert UI after completion ---
            loader.style.display = "none";
            submitButton.disabled = false;
            submitButton.querySelector(".button-text").textContent = "Analyze Culture";
        }
    });
});