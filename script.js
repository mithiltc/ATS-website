let selectedFile = null;

// ----------------------------
// OPEN FILE PICKER
// ----------------------------
function openFilePicker() {
  document.getElementById("resumeInput").click();
}

// ----------------------------
// FILE SELECTION
// ----------------------------
document
  .getElementById("resumeInput")
  .addEventListener("change", function (event) {

    selectedFile = event.target.files[0];

    if (selectedFile) {
      document.getElementById("selectedFile").innerText =
        selectedFile.name;
    }
  });

// ----------------------------
// ANALYZE RESUME
// ----------------------------
async function analyzeResume() {

  if (!selectedFile) {
    alert("Please upload a resume first");
    return;
  }

  // Get Input Values
  const companyName =
    document.getElementById("companyName").value;

  const userName =
    document.getElementById("userName").value;

  const jobDescription =
    document.getElementById("jobDescription").value;

  try {

    // Create Form Data
    const formData = new FormData();

    formData.append("resume", selectedFile);
    formData.append("company_name", companyName);
    formData.append("user_name", userName);
    formData.append("job_description", jobDescription);

    // FastAPI Backend URL
    const response = await fetch(
      "http://127.0.0.1:8000/analyze",
      {
        method: "POST",
        body: formData
      }
    );

    // Handle Error
    if (!response.ok) {
      throw new Error("Failed to analyze resume");
    }

    // Convert Response to JSON
    const data = await response.json();

    console.log(data);

    // Update UI
    updateResults(data.result);

  } catch (error) {

    console.error(error);

    alert("Error analyzing resume");
  }
}

// ----------------------------
// UPDATE UI
// ----------------------------
function updateResults(result) {

  const scoreEl =
    document.getElementById("matchScore");

  const matchedEl =
    document.getElementById("matchedSkills");

  const missingEl =
    document.getElementById("missingSkills");

  const recommendationsEl =
    document.getElementById("recommendations");

  // Check Elements
  if (!scoreEl || !matchedEl || !missingEl) {

    console.error("Missing HTML elements");

    return;
  }

  // ----------------------------
  // MATCH SCORE
  // ----------------------------
  scoreEl.innerText =
    result.match_score + "%";

  // ----------------------------
  // MATCHED SKILLS
  // ----------------------------
  matchedEl.innerHTML = "";

  result.skills.forEach(skill => {

    matchedEl.innerHTML += `
      <span class="green-tag">
        ${skill}
      </span>
    `;
  });

  // ----------------------------
  // MISSING SKILLS
  // ----------------------------
  missingEl.innerHTML = "";

  result.weaknesses.forEach(skill => {

    missingEl.innerHTML += `
      <span class="red-tag">
        ${skill}
      </span>
    `;
  });

  // ----------------------------
  // AI RECOMMENDATIONS
  // ----------------------------
  if (recommendationsEl) {

    recommendationsEl.innerHTML = `
      <p style="line-height:1.7">
        ${result.ai_summary}
      </p>
    `;
  }

  // ----------------------------
  // SMOOTH SCROLL
  // ----------------------------
  document
    .getElementById("resultPage")
    .scrollIntoView({
      behavior: "smooth"
    });
}