from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import pdfplumber
import io
import re

app = FastAPI()

# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# ATS SKILLS DATABASE
# -------------------------------
REQUIRED_SKILLS = [
    "python",
    "java",
    "html",
    "css",
    "javascript",
    "react",
    "nodejs",
    "sql",
    "mongodb",
    "machine learning",
    "fastapi",
    "flask",
    "git",
    "github",
    "api",
    "tailwind",
]

# -------------------------------
# HOME ROUTE
# -------------------------------
@app.get("/")
def home():
    return {
        "message": "MYATS Backend Running"
    }


# -------------------------------
# PDF TEXT EXTRACTION
# -------------------------------
def extract_text_from_pdf(pdf_file):

    text = ""

    with pdfplumber.open(pdf_file) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + " "

    return text.lower()


# -------------------------------
# ATS SCORING FUNCTION
# -------------------------------
def calculate_ats_score(resume_text, job_description):

    matched_skills = []

    # Combine JD + Resume
    combined_text = (
        resume_text + " " + job_description.lower()
    )

    for skill in REQUIRED_SKILLS:

        if re.search(
            r"\b" + re.escape(skill) + r"\b",
            combined_text
        ):

            matched_skills.append(skill)

    # Score Calculation
    score = int(
        (len(matched_skills) / len(REQUIRED_SKILLS)) * 100
    )

    # Missing Skills
    missing_skills = [
        skill
        for skill in REQUIRED_SKILLS
        if skill not in matched_skills
    ]

    # Recommendations
    recommendations = []

    if score < 40:
        recommendations.append(
            "Add more technical skills to improve ATS score."
        )

    if "github" not in matched_skills:
        recommendations.append(
            "Add GitHub projects to strengthen your profile."
        )

    if "machine learning" not in matched_skills:
        recommendations.append(
            "Include domain-specific technologies."
        )

    if len(matched_skills) < 5:
        recommendations.append(
            "Optimize your resume with more keywords from the job description."
        )

    return (
        score,
        matched_skills,
        missing_skills,
        recommendations
    )


# -------------------------------
# RESUME ANALYSIS API
# -------------------------------
@app.post("/upload-resume")
async def upload_resume(

    file: UploadFile = File(...),
    company_name: str = "",
    user_name: str = "",
    job_description: str = ""

):

    # -------------------------------
    # FILE VALIDATION
    # -------------------------------
    allowed_types = [
        "application/pdf"
    ]

    if file.content_type not in allowed_types:

        return JSONResponse(
            status_code=400,
            content={
                "error": "Only PDF files are allowed"
            }
        )

    # -------------------------------
    # READ PDF
    # -------------------------------
    contents = await file.read()

    pdf_file = io.BytesIO(contents)

    # -------------------------------
    # EXTRACT TEXT
    # -------------------------------
    resume_text = extract_text_from_pdf(pdf_file)

    if not resume_text.strip():

        return JSONResponse(
            status_code=400,
            content={
                "error": "Unable to extract text from resume"
            }
        )

    # -------------------------------
    # CALCULATE ATS SCORE
    # -------------------------------
    (
        score,
        matched_skills,
        missing_skills,
        recommendations

    ) = calculate_ats_score(
        resume_text,
        job_description
    )

    # -------------------------------
    # RESPONSE
    # -------------------------------
    return {

        "company_name": company_name,

        "user_name": user_name,

        "ATS Score": score,

        "Matched Skills": matched_skills,

        "Missing Skills": missing_skills,

        "Recommendations": recommendations,

        "Resume Preview": resume_text[:1000]

    }