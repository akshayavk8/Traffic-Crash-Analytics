import os
import gdown
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

DB_PATH = "/tmp/traffic_crashes.db"
CSV_PATH = "/tmp/traffic_crashes.csv"
FILE_ID = "1jAFsxF8ri--wYC1A-8k_Otdlf8xfcODN"

@st.cache_resource
def get_engine():
    # Download CSV if not present
    if not os.path.exists(CSV_PATH):
        with st.spinner("Downloading dataset... please wait"):
            gdown.download(
                f"https://drive.google.com/uc?id={FILE_ID}",
                CSV_PATH,
                quiet=False
            )

    # Build DB in chunks if not present
    if not os.path.exists(DB_PATH):
        with st.spinner("Building database in chunks... please wait"):
            engine = create_engine(f"sqlite:///{DB_PATH}")
            chunk_size = 50000  # process 50,000 rows at a time
            first_chunk = True
            for chunk in pd.read_csv(CSV_PATH, chunksize=chunk_size, low_memory=False):
                if first_chunk:
                    chunk.to_sql("CrashTable", con=engine, if_exists="replace", index=False)
                    first_chunk = False
                else:
                    chunk.to_sql("CrashTable", con=engine, if_exists="append", index=False)

    return create_engine(f"sqlite:///{DB_PATH}")

engine = get_engine()

def run_query(sql):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)

# Page config
st.set_page_config(
    page_title="Traffic Crash Analytics",
    page_icon=" * ",
    layout="wide"
)

st.title("Traffic Crash Analytics & Safety Intelligence Platform")
st.markdown("**Chicago Traffic Crash Data | 600,000+ Records**")
st.markdown("---")

def show_section(title, insight, sql):
    st.subheader(title)
    st.caption(f"**Business Insight:** {insight}")
    df = run_query(sql)
    st.dataframe(df, use_container_width=True)
    st.markdown("---")

# Q1
show_section(
    "Q1: Top 5 most dangerous combinations of weather and crash type",
    "Certain weather-crash type combos are disproportionately deadly — helps traffic authorities prioritize safety alerts.",
    """
    SELECT
        WEATHER_CONDITION,
        FIRST_CRASH_TYPE,
        COUNT(*) AS total_crashes
    FROM CrashTable
    GROUP BY WEATHER_CONDITION, FIRST_CRASH_TYPE
    ORDER BY total_crashes DESC
    LIMIT 5
    """
)

# Q2
show_section(
    "Q2: Top 10 streets with the highest number of injury crashes",
    "Targeting these streets for infrastructure upgrades could significantly reduce injuries.",
    """
    SELECT
        STREET_NAME,
        COUNT(*) AS injury_crashes
    FROM CrashTable
    WHERE INJURIES_TOTAL > 0
    GROUP BY STREET_NAME
    ORDER BY injury_crashes DESC
    LIMIT 10
    """
)

# Q3
show_section(
    "Q3: Injury percentage by crash type",
    "High-injury crash types reveal which collision patterns need the most urgent intervention.",
    """
    SELECT
        FIRST_CRASH_TYPE,
        COUNT(*) AS total_crashes,
        SUM(CASE WHEN INJURIES_TOTAL > 0 THEN 1 ELSE 0 END) AS injury_crashes,
        ROUND(
            100.0 * SUM(CASE WHEN INJURIES_TOTAL > 0 THEN 1 ELSE 0 END) / COUNT(*),
        2) AS injury_percentage
    FROM CrashTable
    GROUP BY FIRST_CRASH_TYPE
    ORDER BY injury_percentage DESC
    """
)

# Q4
show_section(
    "Q4: Peak crash hour per month",
    "Understanding monthly peak hours helps optimize traffic enforcement deployment.",
    """
    WITH hourly_counts AS (
        SELECT
            CRASH_MONTH,
            CRASH_HOUR,
            COUNT(*) AS crash_count,
            RANK() OVER (PARTITION BY CRASH_MONTH ORDER BY COUNT(*) DESC) AS rnk
        FROM CrashTable
        WHERE CRASH_MONTH IS NOT NULL
          AND CRASH_HOUR IS NOT NULL
        GROUP BY CRASH_MONTH, CRASH_HOUR
    )
    SELECT CRASH_MONTH, CRASH_HOUR, crash_count
    FROM hourly_counts
    WHERE rnk = 1
    ORDER BY CRASH_MONTH
    """
)

# Q5
show_section(
    "Q5: Top 5 primary causes of nighttime crashes",
    "Nighttime crash causes differ from daytime — targeted awareness campaigns can be designed.",
    """
    SELECT
        PRIM_CONTRIBUTORY_CAUSE,
        COUNT(*) AS crash_count
    FROM CrashTable
    WHERE CRASH_HOUR >= 18
    GROUP BY PRIM_CONTRIBUTORY_CAUSE
    ORDER BY crash_count DESC
    LIMIT 5
    """
)

# Q6
show_section(
    "Q6: Average injuries — daylight vs darkness",
    "Darkness significantly increases injury severity, justifying investment in better street lighting.",
    """
    SELECT
        LIGHTING_CONDITION,
        ROUND(AVG(INJURIES_TOTAL), 3) AS avg_injuries
    FROM CrashTable
    WHERE LIGHTING_CONDITION IN ('DAYLIGHT', 'DARKNESS', 'DARKNESS, LIGHTED ROAD')
    GROUP BY LIGHTING_CONDITION
    ORDER BY avg_injuries DESC
    """
)

# Q7
show_section(
    "Q7: Traffic control device type with the highest average injuries per crash",
    "Businesses and urban planners should consider targeted interventions in areas with bicycle and pedestrian crossing signs, such as improved signage, dedicated infrastructure (e.g., separated bike lanes, raised crosswalks), or increased enforcement, to enhance safety for pedestrians and cyclists.",
    """
    SELECT
        TRAFFIC_CONTROL_DEVICE,
        ROUND(AVG(INJURIES_TOTAL), 3) AS avg_injuries
    FROM CrashTable
    WHERE TRAFFIC_CONTROL_DEVICE IS NOT NULL
    GROUP BY TRAFFIC_CONTROL_DEVICE
    ORDER BY avg_injuries DESC
    LIMIT 10
    """
)

# Q8
show_section(
    "Q8: Top 5 GPS locations with most crashes",
    "These GPS coordinates are prime candidates for speed cameras or traffic calming measures.",
    """
    SELECT
        ROUND(LATITUDE, 4) AS lat,
        ROUND(LONGITUDE, 4) AS lon,
        COUNT(*) AS crash_count
    FROM CrashTable
    WHERE LATITUDE IS NOT NULL AND LONGITUDE IS NOT NULL
    GROUP BY lat, lon
    ORDER BY crash_count DESC
    LIMIT 5
    """
)

# Q9
show_section(
    "Q9: Top 5 streets with highest injury rate (min. 100 crashes)",
    "High injury rate on high-volume streets signals serious safety deficiencies requiring immediate action.",
    """
    SELECT
        STREET_NAME,
        COUNT(*) AS total_crashes,
        SUM(CASE WHEN INJURIES_TOTAL > 0 THEN 1 ELSE 0 END) AS injury_crashes,
        ROUND(100.0 * SUM(CASE WHEN INJURIES_TOTAL > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS injury_rate
    FROM CrashTable
    GROUP BY STREET_NAME
    HAVING COUNT(*) > 100
    ORDER BY injury_rate DESC
    LIMIT 5
    """
)

# Q10
show_section(
    "Q10: Most common crash type per year",
    "Yearly trends in crash types help assess whether safety campaigns have reduced specific collision patterns.",
    """
    WITH yearly_crash AS (
        SELECT
            year,
            FIRST_CRASH_TYPE,
            COUNT(*) AS crash_count,
            RANK() OVER (PARTITION BY year ORDER BY COUNT(*) DESC) AS rnk
        FROM CrashTable
        GROUP BY year, FIRST_CRASH_TYPE
    )
    SELECT year, FIRST_CRASH_TYPE, crash_count
    FROM yearly_crash
    WHERE rnk = 1
    ORDER BY year
    """
)

# Q11
show_section(
    "Q11: Day of the week with the highest average crashes per hour",
    "Weekend vs weekday crash patterns help optimize patrol schedules and emergency response staffing.",
    """
    SELECT
        CRASH_DAY_OF_WEEK,
        ROUND(AVG(CRASHES_PER_HOUR), 2) AS avg_crashes_per_hour
    FROM (
        SELECT
            CRASH_DAY_OF_WEEK,
            CRASH_HOUR,
            COUNT(*) AS CRASHES_PER_HOUR
        FROM CrashTable
        GROUP BY CRASH_DAY_OF_WEEK, CRASH_HOUR
    )
    GROUP BY CRASH_DAY_OF_WEEK
    ORDER BY avg_crashes_per_hour DESC
    """
)

# Q12
show_section(
    "Q12: High-risk time slots",
    "Identifying the deadliest time window allows targeted deployment of traffic enforcement resources.",
    """
    SELECT
        CASE
            WHEN CRASH_HOUR BETWEEN 6 AND 11 THEN 'Morning'
            WHEN CRASH_HOUR BETWEEN 12 AND 17 THEN 'Afternoon'
            WHEN CRASH_HOUR BETWEEN 18 AND 21 THEN 'Evening'
            ELSE 'Night'
        END AS time_slot,
        SUM(CASE WHEN INJURIES_TOTAL > 0 THEN 1 ELSE 0 END) AS injury_crashes
    FROM CrashTable
    GROUP BY time_slot
    ORDER BY injury_crashes DESC
    """
)

# Q13
show_section(
    "Q13: Top 3 contributing causes for each crash type",
    "Knowing crash-type-specific causes allows tailored driver education programs.",
    """
    WITH cause_counts AS (
        SELECT
            FIRST_CRASH_TYPE,
            PRIM_CONTRIBUTORY_CAUSE,
            COUNT(*) AS cause_count,
            ROW_NUMBER() OVER (
                PARTITION BY FIRST_CRASH_TYPE
                ORDER BY COUNT(*) DESC
            ) AS rn
        FROM CrashTable
        GROUP BY FIRST_CRASH_TYPE, PRIM_CONTRIBUTORY_CAUSE
    )
    SELECT FIRST_CRASH_TYPE, PRIM_CONTRIBUTORY_CAUSE, cause_count
    FROM cause_counts
    WHERE rn <= 3
    ORDER BY FIRST_CRASH_TYPE, rn
    """
)

# Q14
show_section(
    "Q14: Year-over-year growth rate of crashes",
    "YoY growth highlights whether road safety is improving or deteriorating over time.",
    """
    WITH yearly AS (
        SELECT year, COUNT(*) AS total_crashes
        FROM CrashTable
        GROUP BY year
    ),
    yearly_with_prev AS (
        SELECT
            year,
            total_crashes,
            LAG(total_crashes) OVER (ORDER BY year) AS prev_year_crashes
        FROM yearly
    )
    SELECT
        year,
        total_crashes,
        prev_year_crashes,
        ROUND(100.0 * (total_crashes - prev_year_crashes)
            / prev_year_crashes, 2) AS yoy_growth_pct
    FROM yearly_with_prev
    WHERE prev_year_crashes IS NOT NULL
    ORDER BY year
    """
)

# Q15
show_section(
    "Q15: Top 10 crash hotspot zones",
    "Zone-level clustering reveals systemic high-risk areas for large-scale safety infrastructure investment.",
    """
    SELECT
        ROUND(LATITUDE, 2) AS zone_lat,
        ROUND(LONGITUDE, 2) AS zone_lon,
        COUNT(*) AS crash_count
    FROM CrashTable
    WHERE LATITUDE IS NOT NULL AND LONGITUDE IS NOT NULL
    GROUP BY zone_lat, zone_lon
    ORDER BY crash_count DESC
    LIMIT 10
    """
)

st.success("All 15 queries executed successfully!")
