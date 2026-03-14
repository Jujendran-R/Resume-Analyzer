# AI Resume Analyzer

An intelligent Python CLI tool and web interface that analyzes resumes using AI and ATS (Applicant Tracking System) optimization. Perfect for job seekers wanting to optimize their resumes for maximum impact.

## Features

✨ **ATS Optimization Scoring**
- Analyze resume structure and formatting for ATS compatibility
- Check for essential keywords and sections
- Identify formatting issues that may cause parsing problems
- Score out of 100 with specific improvement recommendations

🎯 **Job Description Matching**
- Compare resume against specific job descriptions
- Identify matching and missing keywords
- Match technical skills and experience requirements
- Provide percentage-based compatibility score

🤖 **AI-Powered Feedback** (Requires OpenAI or OpenRouter API)
- Get intelligent feedback on resume quality
- Identify strengths in your resume
- Get specific improvement suggestions
- Understand how to better highlight your achievements

📊 **Multiple Resume Comparison**
- Compare multiple resumes side-by-side
- See which resume scores highest for ATS
- Understand relative strengths and weaknesses

🌐 **Web Interface**
- Easy-to-use Gradio interface for resume analysis
- No technical knowledge required
- Real-time analysis results

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project
```bash
cd "d:\AI Resume"
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up OpenAI API (Optional - for AI Features)
```bash
# Copy the environment template
copy .env.example .env

# Edit .env with your API key
# For OpenAI (set from https://platform.openai.com/api-keys):
OPENAI_API_KEY=sk-your-api-key-here

# Or for OpenRouter (set from https://openrouter.ai/keys):
OPENROUTER_API_KEY=sk-or-your-api-key-here
USE_OPENROUTER=true
```

## Usage

### Command Line Interface

#### Basic ATS Analysis
```bash
python main.py --resume my_resume.pdf
```

#### Compare Resume with Job Description
```bash
python main.py --resume my_resume.pdf --job job_description.txt
```

#### Generate AI Feedback
```bash
python main.py --resume my_resume.pdf --ai-feedback
```

#### Compare Multiple Resumes
```bash
python main.py --compare resume1.pdf resume2.pdf resume3.pdf
```

#### Save Report to File
```bash
python main.py --resume my_resume.pdf --output report.json --format json
```

Supported formats: `json`, `txt`, `csv`

### Web Interface (Recommended)

```bash
python app_gradio.py
```

Then open your browser to `http://localhost:7860`

#### Features:
- Upload resume and job description
- Real-time analysis with visual results
- Optional AI-powered feedback
- Easy-to-read formatted results

## Supported File Formats

- **PDF** (.pdf)
- **Microsoft Word** (.docx, .doc)
- **Text** (.txt)

## Configuration

Edit configuration in [src/config.py](src/config.py):

- `OPENAI_MODEL`: Choose between gpt-4, gpt-3.5-turbo, etc.
- `OPENROUTER_MODEL`: Choose between available models on OpenRouter
- `ATS_KEYWORDS`: Customize keyword lists by category
- `MIN_RESUME_LENGTH`: Minimum resume length for analysis
- `ATS_SCORE_EXCELLENT`: Threshold for excellent ATS score

## How It Works

### ATS Analysis
1. **Formatting Check**: Detects problematic formatting (tables, images, special characters)
2. **Length Analysis**: Verifies resume is within ideal word count (300-600 words)
3. **Keyword Detection**: Searches for industry-relevant keywords
4. **Contact Info**: Verifies presence of email, phone, LinkedIn
5. **Section Verification**: Checks for standard resume sections
6. **Metrics Check**: Looks for quantifiable achievements

### Job Matching
1. Extracts keywords from job description
2. Compares them against resume content
3. Calculates match percentage
4. Identifies skills gaps
5. Provides specific recommendations

### AI Analysis (Optional)
1. Sends resume to OpenAI or OpenRouter API
2. Gets expert feedback on resume quality
3. Identifies strengths and improvement areas
4. Provides actionable recommendations
5. Scores overall resume quality

## Examples

### Example 1: Quick Analysis
```bash
python main.py --resume samples/sample_resume.txt
```

Output:
```
ATS Score: 78/100 (Grade: B)
- Resume length optimal: 450 words ✓
- Found sections: experience, education, skills ✓
- Missing contact information (email, phone, LinkedIn): email detected ✓
- Found 25 relevant keywords
```

### Example 2: Job Matching
```bash
python main.py --resume my_resume.txt --job job_posting.txt
```

Output:
```
Job Match: 72%
Matched Keywords: 18/25
- You have these skills: Python, React, AWS, Docker
- You're missing: Kubernetes, GraphQL, Machine Learning
```

### Example 3: With AI Feedback
```bash
python main.py --resume my_resume.txt --ai-feedback
```

Output:
```
AI Quality Score: 82/100

Strengths:
- Clear structure with well-defined sections
- Good use of metrics and achievements
- Relevant technical keywords

Improvements:
- Add more quantifiable results
- Improve action verbs in bullet points
```

## Troubleshooting

### Issue: "No module named 'PyPDF2'"
**Solution:** Run `pip install PyPDF2`

### Issue: "OpenAI API key not found"
**Solution:** Create `.env` file with your API key:
```
OPENAI_API_KEY=sk-your-key-here
```

### Issue: "Resume file not found"
**Solution:** Provide full path to resume file:
```bash
python main.py --resume "C:\Documents\resume.pdf"
```

### Issue: Gradio server won't start
**Solution:** Check if port 7860 is available. Modify in `app_gradio.py` if needed.

## Project Structure

```
AI Resume/
├── main.py                 # CLI entry point
├── app_gradio.py          # Web interface
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── src/
│   ├── config.py          # Configuration settings
│   ├── resume_parser.py   # Parse resume files
│   ├── ats_analyzer.py    # ATS analysis logic
│   ├── job_matcher.py     # Job matching logic
│   ├── ai_analyzer.py     # AI-powered analysis
│   └── report_generator.py # Report generation
├── samples/
│   ├── sample_resume.txt
│   └── sample_job_description.txt
├── tests/                 # Test files
└── config/               # Configuration files
```

## Performance Tips

- For PDF files over 5 MB, conversion may take longer
- AI analysis requires internet connection and API calls
- Large batch comparisons may take a few minutes

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please check the troubleshooting section or create an issue in the repository.

## Changelog

### Version 1.0.0 (Initial Release)
- ATS analysis and scoring
- Job description matching
- AI-powered feedback integration
- CLI and web interface
- Report generation (JSON, TXT, CSV)
- Multi-file comparison

---

**Pro Tips:**
- Use consistent formatting and clear section headers
- Include both hard skills (technical) and soft skills
- Add metrics and quantifiable achievements
- Tailor your resume for each job application
- Keep it to 1-2 pages (3 for very experienced professionals)
