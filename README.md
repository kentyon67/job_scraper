# JobFit

JobFit is a Python-based job scraping and AI analysis app built to help users compare engineering job postings more efficiently.

It collects job listings, extracts job details, enriches them with AI-generated summaries / translations / classifications / scores, and presents them through a Streamlit UI.

## Features

- Scrape job list pages and job detail pages
- Retry failed detail fetches
- Build structured CSV datasets
- AI-generated summary
- Japanese translation for UI display
- Job category / Python-related / AI-related classification
- Score jobs by market value and user fit
- Compare jobs in a Streamlit list UI
- View detailed job information
- Edit user profile preferences in UI

## Project Structure

```text
src/
  app.py
  pipeline.py
  fetch_list.py
  fetch_detail.py
  retry_failed.py
  build_dataset.py
  utils.py
  user_profile.py
  pages/
    job_detail.py
    profile_settings.py
  ai/
    summarize.py
    translate.py
    classify.py
    score.py
    compare.py
    export_detail.py

data/
  raw/
  output/
  logs/


Tech Stack
Python
Streamlit
pandas
requests
BeautifulSoup
lxml
OpenAI API
Setup
1. Clone repository
git clone <your-repo-url>
cd <your-repo-name>
2. Create virtual environment
python -m venv .venv
3. Activate virtual environment
Windows PowerShell
.venv\Scripts\Activate.ps1
macOS / Linux
source .venv/bin/activate
4. Install dependencies
pip install -r requirements.txt
5. Set OpenAI API key
Windows PowerShell
$env:OPENAI_API_KEY="your_api_key"
macOS / Linux
export OPENAI_API_KEY="your_api_key"
How to Run
Run data pipeline
python -m src.cli pipeline --mode full --max-jobs 5
Run Streamlit app
streamlit run src/app.py
Deployment

This app can be deployed on Streamlit Community Cloud.

For public demo deployment, the recommended approach is:

Generate CSV files locally in advance
Push the generated data/output/*.csv
Deploy only the Streamlit UI for viewing

This avoids exposing API-based analysis in the public app runtime.

Notes
OPENAI_API_KEY is required only for AI enrichment steps
Public UI deployment can work without API calls if output CSV files are already prepared
This project is currently designed around Greenhouse-style job pages and is planned to expand to multi-company / multi-source search in future versions
Future Improvements
Search-based UI
Multi-company support
Multi-language job support
Database integration
API backend
Scheduled updates
Author

Built as a portfolio project for internship-ready Python engineering work.

Tech Stack
Python
Streamlit
pandas
requests
BeautifulSoup
lxml
OpenAI API
Setup
1. Clone repository
git clone <your-repo-url>
cd <your-repo-name>
2. Create virtual environment
python -m venv .venv
3. Activate virtual environment
Windows PowerShell
.venv\Scripts\Activate.ps1
macOS / Linux
source .venv/bin/activate
4. Install dependencies
pip install -r requirements.txt
5. Set OpenAI API key
Windows PowerShell
$env:OPENAI_API_KEY="your_api_key"
macOS / Linux
export OPENAI_API_KEY="your_api_key"
How to Run
Run data pipeline
python -m src.cli pipeline --mode full --max-jobs 5
Run Streamlit app
streamlit run src/app.py
Deployment

This app can be deployed on Streamlit Community Cloud.

For public demo deployment, the recommended approach is:

Generate CSV files locally in advance
Push the generated data/output/*.csv
Deploy only the Streamlit UI for viewing

This avoids exposing API-based analysis in the public app runtime.

Notes
OPENAI_API_KEY is required only for AI enrichment steps
Public UI deployment can work without API calls if output CSV files are already prepared
This project is currently designed around Greenhouse-style job pages and is planned to expand to multi-company / multi-source search in future versions
Future Improvements
Search-based UI
Multi-company support
Multi-language job support
Database integration
API backend
Scheduled updates
Author

Built as a portfolio project for internship-ready Python engineering work.