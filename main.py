from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
import anthropic
import io

app = FastAPI()

# -----------------------------
# Enable CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Claude API Client
# -----------------------------
client = anthropic.Anthropic(
    api_key="your-api-key-here"
)

# -----------------------------
# Home Route
# -----------------------------
@app.get("/")
async def home():
    return {
        "message": "ATS Backend Running"
    }


# -----------------------------
# Analyze Resume Route
# -----------------------------
@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(default="")
):

    if not resume:
        return JSONResponse(
            status_code=400,
            content={"error": "No resume uploaded"}
        )

    # -----------------------------
    # Extract PDF Text
    # -----------------------------
    text = ""

    try:
        pdf_bytes = await resume.read()
        pdf_stream = io.BytesIO(pdf_bytes)

        reader = PdfReader(pdf_stream)

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

    # -----------------------------
    # Skills List
    # -----------------------------
    skills = [
        # Programming
        "python", "java", "javascript", "typescript", "c++", "c#", "r", "kotlin", "swift",

        # Web
        "html", "css", "react", "angular", "vue", "node", "flask", "django", "fastapi",

        # Data
        "sql", "mysql", "postgresql", "mongodb", "excel", "tableau", "power bi",

        # Cloud & Tools
        "aws", "azure", "docker", "git", "linux", "api", "rest",

        # Soft Skills
        "communication", "leadership", "teamwork", "management", "problem solving",

        # General
        "machine learning",
        "deep learning",
        "data analysis",
        "project management"
    ]

    # -----------------------------
    # Skill Matching
    # -----------------------------
    matched_skills = [
        skill for skill in skills
        if skill.lower() in text.lower()
    ]

    missing_skills = [
        skill for skill in skills
        if skill.lower() not in text.lower()
    ]

    # -----------------------------
    # ATS Score Calculation
    # -----------------------------
    if job_description:

        jd_skills = [
            skill for skill in skills
            if skill.lower() in job_description.lower()
        ]

        if jd_skills:
            jd_matches = [
                skill for skill in jd_skills
                if skill.lower() in text.lower()
            ]

            score = int(
                (len(jd_matches) / len(jd_skills)) * 100
            )

        else:
            score = int(
                (len(matched_skills) / len(skills)) * 100
            )

    else:
        score = int(
            (len(matched_skills) / len(skills)) * 100
        )

    # -----------------------------
    # AI Summary using Claude
    # -----------------------------
    try:

        prompt = f"""
You are an ATS assistant. A resume was analyzed.

- ATS Match Score: {score}%
- Matched Skills: {", ".join(matched_skills) if matched_skills else "None"}
- Missing Skills: {", ".join(missing_skills) if missing_skills else "None"}
- Job Description: {job_description if job_description else "Not provided"}

Give a short 3-5 sentence friendly summary:
1. What skills the candidate has
2. How well they match the job
3. What they should improve
"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        ai_summary = message.content[0].text

    except Exception as e:
        ai_summary = f"AI summary unavailable: {str(e)}"

    # -----------------------------
    # Final Response
    # -----------------------------
    return {
        "result": {
            "match_score": f"{score}",
            "skills": matched_skills,
            "weaknesses": missing_skills,
            "strengths": [
                "Resume successfully analyzed",
                "Skill matching completed",
                "ATS screening ready"
            ],
            "ai_summary": ai_summary
        }
    }


# -----------------------------
# Run Server
# -----------------------------
# Run using:
# uvicorn main:app --reload