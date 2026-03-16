import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-3-27b-it:free")
USE_OPENROUTER = os.getenv("USE_OPENROUTER", "true").lower() == "true"

UPLOAD_FOLDER = Path("/tmp/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
# ATS Keywords
ATS_KEYWORDS = {
    "technical": [
        "python", "java", "javascript", "c++", "c#", "sql", "react", "nodejs",
        "aws", "docker", "kubernetes", "git", "agile", "rest api", "microservices",
        "machine learning", "ai", "deep learning", "tensorflow", "pytorch",
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "problem-solving", "project management",
        "analytical skills", "critical thinking", "time management", "adaptability",
    ],
}

ATS_SCORE_EXCELLENT = 80
ATS_SCORE_GOOD = 60
ATS_SCORE_FAIR = 40


class ResumeParser:
    """Parse resume files in different formats."""
    
    SUPPORTED_FORMATS = {".txt", ".pdf", ".docx", ".doc"}
    
    @staticmethod
    def parse_file(file_path: str) -> str:
        """Parse a resume file and extract text."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        file_ext = path.suffix.lower()
        
        if file_ext not in ResumeParser.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {file_ext}")
        
        if file_ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif file_ext == ".pdf":
            try:
                import PyPDF2
                text = ""
                with open(file_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                return text
            except ImportError:
                raise ImportError("PyPDF2 not installed")
        elif file_ext in {".docx", ".doc"}:
            try:
                from docx import Document
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except ImportError:
                raise ImportError("python-docx not installed")


class ATSAnalyzer:
    """Analyze resume for ATS compatibility."""
    
    def __init__(self, resume_text: str):
        self.resume_text = resume_text.lower()
        self.score = 0
        self.issues = []
        self.found_keywords = []
    
    def analyze(self) -> Dict:
        """Perform comprehensive ATS analysis."""
        self.score = 0
        self.issues = []
        self.found_keywords = []
        
        self._check_formatting()
        self._check_length()
        self._check_keywords()
        self._check_contact_info()
        self._check_sections()
        self._check_numbers_and_metrics()
        
        self.score = min(100, max(0, self.score))
        
        return {
            "ats_score": self.score,
            "percentage": round((self.score / 100) * 100, 2),
            "grade": self._get_grade(),
            "issues": self.issues,
            "found_keywords": self.found_keywords,
            "recommendations": self._generate_recommendations()
        }
    
    def _get_grade(self) -> str:
        if self.score >= ATS_SCORE_EXCELLENT:
            return "A"
        elif self.score >= ATS_SCORE_GOOD:
            return "B"
        elif self.score >= ATS_SCORE_FAIR:
            return "C"
        else:
            return "D"
    
    def _check_formatting(self):
        points = 0
        if not re.search(r'(\|.*\||\+.*\+|┌|─|┐)', self.resume_text):
            points += 10
        
        if not re.search(r'\b(image|figure|graphic|chart|photo)\b', self.resume_text):
            points += 5
        
        self.score += points
    
    def _check_length(self):
        text_length = len(self.resume_text.split())
        points = 0
        
        if 300 <= text_length <= 600:
            points = 15
            self.issues.append(f"✅ Resume length optimal: {text_length} words")
        elif 200 <= text_length < 300:
            points = 10
            self.issues.append(f"⚠️ Resume is short ({text_length} words). Add more details.")
        elif 600 < text_length <= 1000:
            points = 12
            self.issues.append(f"⚠️ Resume is long ({text_length} words). Prefer 300-600 words.")
        else:
            points = 5
            self.issues.append(f"❌ Resume is very short. Add more content.")
        
        self.score += points
    
    def _check_keywords(self):
        points = 0
        found_categories = {}
        
        for category, keywords in ATS_KEYWORDS.items():
            category_matches = []
            for keyword in keywords:
                if keyword in self.resume_text:
                    category_matches.append(keyword)
                    points += 1
            
            if category_matches:
                found_categories[category] = category_matches
        
        points = min(20, points)
        self.found_keywords = found_categories
        self.score += points
    
    def _check_contact_info(self):
        points = 0
        contact_elements = {
            "email": r'\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "linkedin": r'linkedin\.com|linkedin',
        }
        
        found_contact = []
        for contact_type, pattern in contact_elements.items():
            if re.search(pattern, self.resume_text):
                found_contact.append(contact_type)
                points += 5
        
        if len(found_contact) < 2:
            self.issues.append(f"⚠️ Add missing contact info")
        else:
            self.issues.append(f"✅ Contact info found: {', '.join(found_contact)}")
        
        self.score += points
    
    def _check_sections(self):
        required_sections = {
            "experience": r'\b(experience|employment|work|professional)\b',
            "education": r'\b(education|degree|university|college|school)\b',
            "skills": r'\b(skills|technical skills|competencies)\b',
        }
        
        points = 0
        found_sections = []
        
        for section, pattern in required_sections.items():
            if re.search(pattern, self.resume_text):
                points += 8
                found_sections.append(section)
            else:
                self.issues.append(f"⚠️ Missing '{section}' section.")
        
        if found_sections:
            self.issues.append(f"✅ Found sections: {', '.join(found_sections)}")
        
        self.score += points
    
    def _check_numbers_and_metrics(self):
        metrics_score = 0
        
        percentages = len(re.findall(r'\b(\d+)%', self.resume_text))
        metrics_score += min(5, percentages)
        
        currency = len(re.findall(r'\$\d+|budget|\brevenue\b', self.resume_text))
        metrics_score += min(5, currency)
        
        numbers = len(re.findall(r'\b\d{2,}\b', self.resume_text))
        metrics_score += min(5, numbers // 3)
        
        if metrics_score == 0:
            self.issues.append("⚠️ Add metrics and numbers to show impact.")
        else:
            self.issues.append(f"✅ Found {percentages + currency} quantifiable metrics.")
        
        self.score += metrics_score
    
    def _generate_recommendations(self) -> List[str]:
        if self.score < 50:
            return ["Major improvements needed. Add contact info, clear structure, keywords."]
        elif self.score < 70:
            return ["Moderate improvements recommended. Focus on keywords and metrics."]
        else:
            return ["Resume is in good shape!"]


class JobMatcher:
    """Match resume against job description."""
    
    def __init__(self, resume_text: str, job_description: str):
        self.resume_text = resume_text.lower()
        self.job_description = job_description.lower()
    
    def match(self) -> Dict:
        """Perform job matching."""
        matched_keywords = self._find_matched_keywords()
        missing_keywords = self._find_missing_keywords()
        match_percentage = self._calculate_match_percentage(matched_keywords, missing_keywords)
        
        return {
            "match_percentage": match_percentage,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "total_keywords": len(matched_keywords) + len(missing_keywords),
            "matched_count": len(matched_keywords),
            "missing_count": len(missing_keywords),
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        keywords = re.findall(r'\b[a-z0-9\+#\-]+\b', text)
        
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'be', 'is', 'are', 'required', 'experience', 'job'
        }
        
        filtered_keywords = []
        seen = set()
        for kw in keywords:
            if len(kw) > 2 and kw not in common_words and kw not in seen:
                filtered_keywords.append(kw)
                seen.add(kw)
        
        return filtered_keywords[:50]
    
    def _find_matched_keywords(self) -> List[str]:
        job_keywords = self._extract_keywords(self.job_description)
        matched = [kw for kw in job_keywords if kw in self.resume_text]
        return sorted(list(set(matched)))
    
    def _find_missing_keywords(self) -> List[str]:
        job_keywords = self._extract_keywords(self.job_description)
        missing = [kw for kw in job_keywords if kw not in self.resume_text]
        return sorted(list(set(missing)))
    
    def _calculate_match_percentage(self, matched: List[str], missing: List[str]) -> float:
        total = len(matched) + len(missing)
        if total == 0:
            return 0.0
        return round((len(matched) / total) * 100, 2)


class AIAnalyzer:
    """AI-powered resume analysis."""
    
    def __init__(self, resume_text: str):
        self.resume_text = resume_text
        self.api_key = None
        self.model = None
        self.provider = None
        self._setup_api()
    
    def _setup_api(self):
        """Setup API configuration."""
        if USE_OPENROUTER and OPENROUTER_API_KEY:
            self.api_key = OPENROUTER_API_KEY
            self.model = OPENROUTER_MODEL
            self.provider = "openrouter"
        elif OPENAI_API_KEY:
            self.api_key = OPENAI_API_KEY
            self.model = OPENAI_MODEL
            self.provider = "openai"
        else:
            raise ValueError("No API key configured")
    
    def analyze(self) -> Dict:
        """Get AI feedback on resume."""
        try:
            if self.provider == "openrouter":
                return self._analyze_with_openrouter()
            elif self.provider == "openai":
                return self._analyze_with_openai()
        except Exception as e:
            return self._generate_fallback_feedback()
    
    def _analyze_with_openrouter(self) -> Dict:
        """Analyze using OpenRouter API."""
        try:
            import requests
            
            prompt = self._create_analysis_prompt()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/user/ai-resume-analyzer",
                "X-Title": "AI Resume Analyzer"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert resume reviewer."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "max_tokens": 1200,
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code != 200:
                return self._generate_fallback_feedback()
            
            content = response.json()["choices"][0]["message"]["content"]
            return self._parse_ai_response(content)
        except Exception as e:
            return self._generate_fallback_feedback()
    
    def _analyze_with_openai(self) -> Dict:
        """Analyze using OpenAI API."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            prompt = self._create_analysis_prompt()
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1200
            )
            
            return self._parse_ai_response(response.choices[0].message.content)
        except Exception as e:
            return self._generate_fallback_feedback()
    
    def _create_analysis_prompt(self) -> str:
        """Create analysis prompt."""
        return f"""Please analyze this resume:

RESUME:
{self.resume_text[:2000]}

Provide feedback in this format:
ASSESSMENT: [1-2 sentences]
STRENGTHS:
- [Strength 1]
- [Strength 2]
- [Strength 3]
IMPROVEMENTS:
- [Improvement 1]
- [Improvement 2]
- [Improvement 3]
SCORE: [Score]/100"""
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response."""
        result = {
            "summary": response_text,
            "strengths": [],
            "improvements": [],
            "score": 75
        }
        
        try:
            lines = response_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith("ASSESSMENT:"):
                    result["summary"] = line.replace("ASSESSMENT:", "").strip()
                elif line.startswith("STRENGTHS:"):
                    current_section = "strengths"
                elif line.startswith("IMPROVEMENTS:"):
                    current_section = "improvements"
                elif line.startswith("SCORE:"):
                    try:
                        score_text = line.replace("SCORE:", "").strip()
                        result["score"] = int(score_text.split('/')[0])
                    except:
                        result["score"] = 75
                elif line.startswith("- ") and current_section:
                    item = line[2:].strip()
                    if item:
                        result[current_section].append(item)
            
            if not result["strengths"]:
                result["strengths"] = ["Resume shows professional structure."]
            if not result["improvements"]:
                result["improvements"] = ["Add more quantifiable achievements."]
                
        except Exception as e:
            pass
        
        return result
    
    def _generate_fallback_feedback(self) -> Dict:
        """Generate basic feedback as fallback."""
        text = self.resume_text.lower()
        
        strengths = []
        improvements = []
        score = 50
        
        if len(self.resume_text) > 500:
            strengths.append("Resume has adequate length")
            score += 10
        
        if any(word in text for word in ["led", "managed", "implemented"]):
            strengths.append("Uses strong action verbs")
            score += 10
        
        if any(word in text for word in ["%", "million", "$"]):
            strengths.append("Includes metrics")
            score += 10
        else:
            improvements.append("Add more numbers and metrics")
        
        if not strengths:
            strengths.append("Resume has professional structure.")
        
        score = min(100, score)
        
        return {
            "summary": "Basic analysis: Resume shows professional structure.",
            "strengths": strengths[:3],
            "improvements": improvements[:3],
            "score": score
        }


@app.route("/")
def index():
    """Serve main page."""
    return render_template("index.html")

@app.route("/health")
def health():
    return "OK", 200

@app.route("/kaithheathcheck")
def kaithheathcheck():
    return "OK", 200


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze resume."""
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No resume file uploaded"}), 400
        
        resume_file = request.files['resume']
        job_file = request.files.get('job_description')
        
        if resume_file.filename == '':
            return jsonify({"error": "No resume file selected"}), 400
        
        # Save uploaded files
        resume_filename = secure_filename(resume_file.filename)
        resume_path = Path(app.config['UPLOAD_FOLDER']) / resume_filename
        resume_file.save(str(resume_path))
        
        job_path = None
        if job_file and job_file.filename != '':
            job_filename = secure_filename(job_file.filename)
            job_path = Path(app.config['UPLOAD_FOLDER']) / job_filename
            job_file.save(str(job_path))
        
        # Parse resume
        parser = ResumeParser()
        resume_text = parser.parse_file(str(resume_path))
        
        # ATS Analysis
        ats_analyzer = ATSAnalyzer(resume_text)
        ats_results = ats_analyzer.analyze()
        
        # Job Matching
        job_results = None
        if job_path:
            job_text = Path(job_path).read_text(encoding="utf-8")
            job_matcher = JobMatcher(resume_text, job_text)
            job_results = job_matcher.match()
        
        # AI Analysis
        ai_results = None
        try:
            ai_analyzer = AIAnalyzer(resume_text)
            ai_results = ai_analyzer.analyze()
        except Exception as e:
            ai_results = {"error": str(e), "score": 60}
        
        return jsonify({
            "ats": ats_results,
            "job_matching": job_results,
            "ai_feedback": ai_results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)