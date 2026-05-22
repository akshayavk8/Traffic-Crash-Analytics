# Traffic-Crash-Analytics
## Overview
SQL-based analysis of 600,000+ Chicago traffic crashes using Python, SQLite, and Streamlit.

## Dataset
- Source: Chicago Data Portal
- Records: 600,000+
- Time Range: 2015–present
- Table Name: CrashTable

## Dataset File
The dataset file (600,000+ rows) and database file are too large for GitHub's file limit. The Streamlit app automatically downloads the dataset from Google Drive and builds the database on first run.
Download dataset (.csv) here: [Traffic_CrashesData.csv](https://drive.google.com/file/d/15ELFc29M1NFv550rhTfxFvY_YRG8waLM/view?usp=sharing)
Download database file (.db) here: [traffic_crashes.db](https://drive.google.com/file/d/1b7TW2m9z7lrl2RRzMkM4fODx7BW1fL1i/view?usp=sharing)

## Project Structure
| File | Description |
|------|-------------|
| `TrafficCrashAnalytics.ipynb` | Full analysis notebook with all 15 queries |
| `Traffic_CrashesData.csv` | Dataset file |
| `traffic_crashes.db` | SQLite database file |
| `app.py` | Streamlit dashboard |
| `requirements.txt` | Required libraries |
| `query_results/` | CSV exports of all 15 query outputs |

## SQL Concepts Used
- Aggregations (COUNT, SUM, AVG)
- Window Functions (RANK, ROW_NUMBER, LAG)
- CTEs (Common Table Expressions)
- Subqueries
- CASE WHEN
- HAVING

## Live App
[Click here to view the Streamlit app](your-streamlit-link-here)
