# 📈 META Ad Data Analysis Platform

Welcome to the **Meta Ad Data Analysis Platform**—a cloud-powered pipeline that transforms raw META (Facebook/Instagram) ad exports into structured insights, slick visuals, and business-ready reports.

---

## 🚀 What’s This Platform For?

This platform is built to help marketers, analysts, and growth hackers extract **meaningful insights** from recurring ad campaign data. Whether you’re tracking *quote rates*, *cost-per-result*, or *Instagram profile visits*, this end-to-end pipeline handles it all—automatically.

Use it to:
- 💡 Understand asset-level ad performance across time.
- 📊 Compare campaigns via SQL-powered analysis.
- 🧺 Store structured datasets in a cloud-based RDS.
- 📁 Generate daily/weekly/monthly reports for decision-makers.

---

## 🛠️ Platform Architecture

```
META Ads Export (.csv)
        ⬇
    ✅ Upload to S3
        ⬇
🪂 AWS Lambda Triggered
        ⬇
🤖 SageMaker Processing Job
        ⬇
📊 PostgreSQL (RDS) Database
        ⬇
📤 SQL-Based Analysis + Reports
        ⬇
📝 Text & PNG Reports (with timestamps)
```

---

## ☁️ Cloud Tools Used

| Service           | Role                                                          |
|------------------|---------------------------------------------------------------|
| **S3**           | Stores raw and preprocessed ad data files                     |
| **Lambda**       | Detects new uploads and triggers processing jobs              |
| **SageMaker**    | Runs Python scripts for data cleaning + analysis              |
| **PostgreSQL RDS** | Stores structured campaign data for SQL-based querying        |
| **QuickSight / Power BI** *(optional)* | Visualizes data over time                            |

---

## 📦 Project Structure

```
📁 Ad-Data-Analysis-Lingerie/
├── data/                   # Local data folder (optional)
├── models/                 # Model-related files (future use)
├── reports/                # Generated .txt + .png reports
├── scripts/                # Lambda + trigger scripts
├── src/
│   ├── preprocessor/
│   │   ├── core.py         # Main orchestrator
│   │   └── steps/          # Modular cleaning functions
│   └── analyser/
│       ├── core.py         # SQL analysis orchestration
│       └── sql_metrics.py  # Defined SQL-based metrics
├── function_test.ipynb     # Manual test harness
├── notebook_taskher_analysis.ipynb # EDA + experimentation
├── requirements.txt        # Pip dependencies
└── main.py                 # Pipeline entry point
```

---

## 🧪 Installation & Setup

> **Pre-req:** Python 3.10+, PostgreSQL running (AWS RDS or local), AWS CLI configured

1. **Clone the repo:**
   ```bash
   git clone https://github.com/yourusername/ad-data-analysis.git
   cd ad-data-analysis
   ```

2. **Install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   Either create a `.env` file or configure AWS credentials + DB URI manually in your code.

4. **Trigger the pipeline:**
   - **Manual:** Run `main.py` after placing raw `.csv` in your S3 bucket.
   - **Auto:** Use your Lambda trigger (already preconfigured) to auto-process uploads.

---

## 📊 What Does It Analyze?

Metrics currently supported:
- **Cost Per Quote** by ad asset type
- **Cost Per Result** by campaign objective
- **Quote Rates**, **Lead Rates**, **CTR (%)**, **Instagram Visit Rates**
- Automatically calculates time-based performance summaries.

All outputs are stored in `reports/` with timestamped filenames.

---

## 🔮 Future Additions

- ✨ Power BI / QuickSight Dashboards
- 📈 Time series modeling for quote predictions
- 🧠 Embedding performance metrics for LLM-powered campaign summaries
- ⏳ Append vs. Table-per-batch strategies for advanced archiving

---

## 🧠 Who Is This For?

This platform is ideal for:
- ✨ **Marketing teams** running frequent META ad campaigns
- 📊 **Data scientists** looking to automate social ad analytics
- 🧪 **Startups** building pipelines around paid acquisition
- 🕵️ **Analysts** tired of manually wrangling ad CSVs every Monday

---

## 🤝 Contributing

Pull requests are welcome! If you’ve got new metrics, visualization templates, or data integrations, send ‘em in. Let’s build the **Ad Oracle** we deserve.

---

## 🧙‍♂️ Maintainer

Crafted by [Keith Arogo Owino](https://keitharogo.github.io/)  
