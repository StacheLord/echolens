# 🧠 EchoLens

EchoLens is an advanced news comparison and fact-checking tool built with Python and Streamlit.  
It allows users to analyze a news article, find related articles across multiple sources, compare intricate claims, and validate details against fact-checking databases.

---

## 🚀 Features

- 📥 Extracts original news article content from a URL
- 🔍 Finds related articles across the web
- 🧩 Matches claims and key phrases across articles
- 🕵️ Checks against Google Fact Check API (optional)
- 📊 Provides an interactive, filterable dashboard
- 📝 Visual side-by-side article comparison with fact fragment highlighting
- 📄 Downloadable CSV comparison exports
- 🧠 Boolean keyword search support (AND, OR, NOT)

---

## 🌐 Live Demo

👉 [Launch EchoLens](https://your-render-deployment-link-here)  
*(Replace this link with your Render URL!)*

---

## 🛠 Installation (Local Development)

**Clone Repo**
git clone https://github.com/yourusername/echolens.git
cd echolens

**Create and activate virtual environment**
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

**Install required packages**
pip install -r requirements.txt

**Run the app**
streamlit run echolens_streamlit_ui.py

🔑 API Keys
Google Fact Check API Key (optional for fact-checking)
Set the API key as an environment variable called FACT_CHECK_API_KEY, or define it inside Streamlit Secrets.

**LICENSE**
This project is protected under copyright.
Duplication, modification, or use of EchoLens for financial gain without written permission is prohibited.

🙏 Acknowledgements
Built with ❤️ using Streamlit, spaCy, and Newspaper3k.

Thanks to all open-source contributors and news fact-checking projects.

