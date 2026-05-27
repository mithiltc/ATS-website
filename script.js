document
  .getElementById("resumeInput")
  .addEventListener("change", function () {

    const file = this.files[0];

    if (file) {
      document.getElementById(
        "selectedFile"
      ).innerText = file.name;
    }
});


async function analyzeResume() {

    const fileInput =
        document.getElementById("resumeInput");

    const file = fileInput.files[0];

    if (!file) {

        alert("Please upload a resume");

        return;
    }

    const formData = new FormData();

    formData.append("file", file);

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/upload-resume",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        console.log(data);

        // Show result page
        document
          .getElementById("resultPage")
          .style.display = "block";

        // Update score
        document.getElementById(
          "matchScore"
        ).innerText = data["ATS Score"] + "%";

        // Matched skills
        const matchedSkills =
            document.getElementById("matchedSkills");

        matchedSkills.innerHTML = "";

        data["Matched Skills"].forEach(skill => {

            matchedSkills.innerHTML += `
                <span class="skill-tag">
                    ${skill}
                </span>
            `;
        });

        // Missing skills
        const missingSkills =
            document.getElementById("missingSkills");

        missingSkills.innerHTML = "";

        data["Missing Skills"].forEach(skill => {

            missingSkills.innerHTML += `
                <span class="missing-tag">
                    ${skill}
                </span>
            `;
        });

    } catch (error) {

        console.error(error);

        alert("Error connecting to backend");
    }
}