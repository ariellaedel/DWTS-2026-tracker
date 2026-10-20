import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="DWTS Analytics Dashboard", layout="wide")
st.title("💃 Dancing with the Stars Dashboard")

# Load data using numpy_nullable backend
df = pd.read_csv("dwts_data.csv", dtype_backend="numpy_nullable")
df.columns = df.columns.str.strip()

# Smart auto-fix for column name variations
column_mapping = {}
for col in df.columns:
    col_lower = col.lower()
    if "celebf" in col_lower or "name" in col_lower or "couple" in col_lower or "celebrity" in col_lower:
        column_mapping[col] = "Celebrity"
    elif "week" in col_lower or "wk" in col_lower:
        column_mapping[col] = "Week"
    elif "score" in col_lower or "point" in col_lower or "total" in col_lower:
        column_mapping[col] = "Score"
    elif "season" in col_lower:
        column_mapping[col] = "Season"

df = df.rename(columns=column_mapping)

# Remove any duplicate columns if multiple matched the same name
df = df.loc[:, ~df.columns.duplicated()]

# Ensure required columns exist
required_cols = ["Celebrity", "Week", "Score"]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"Missing required columns: {missing}. Found columns in your CSV: {list(df.columns)}")
    st.stop()

# Safety check: if Celebrity is somehow still a table, grab the first column
if isinstance(df["Celebrity"], pd.DataFrame):
    df["Celebrity"] = df["Celebrity"].iloc[:, 0]

# Robust score cleaning and max score detection (handles /40 for Week 4, /30, etc.)
earned_scores = []
max_scores = []

for idx, row in df.iterrows():
    val_str = str(row["Score"]).strip()
    week_val = row.get("Week", None)
    
    earned = None
    possible = None
    
    if "/" in val_str:
        parts = [p.strip() for p in val_str.split("/") if p.strip() != ""]
        if len(parts) >= 2:
            earned = pd.to_numeric(parts[0], errors="coerce")
            possible = pd.to_numeric(parts[1], errors="coerce")
        elif len(parts) == 1:
            earned = pd.to_numeric(parts[0], errors="coerce")
    else:
        earned = pd.to_numeric(val_str, errors="coerce")
        
    # Default max score logic if not explicitly in the fraction
    if pd.isna(possible):
        # If week is 4 (or user noted week 4 is out of 40), default to 40, otherwise 30
        if str(week_val) == "4":
            possible = 40
        else:
            possible = 30
            
    earned_scores.append(earned)
    max_scores.append(possible)

df["Score"] = pd.Series(earned_scores, dtype="float64")
df["Max_Score"] = pd.Series(max_scores, dtype="float64")
df["Percentage"] = (df["Score"] / df["Max_Score"]) * 100
df["Week"] = pd.to_numeric(df["Week"], errors="coerce")

# Sidebar Filters
st.sidebar.header("Filter Options")
selected_celebrity = st.sidebar.multiselect(
    "Select Celebrity:",
    options=df["Celebrity"].unique(),
    default=df["Celebrity"].unique(),
)

score_display_mode = st.sidebar.radio(
    "Display Score Metric:",
    ["Raw Points Earned", "Percentage (%)"]
)

filtered_df = df[df["Celebrity"].isin(selected_celebrity)].sort_values(by="Week")

# Choose metric column based on sidebar selection
metric_col = "Score" if score_display_mode == "Raw Points Earned" else "Percentage"
metric_label = "Average Score (Points)" if score_display_mode == "Raw Points Earned" else "Average Performance (%)"

# Metrics with safe average calculation
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Performances Tracked", len(filtered_df))
with col2:
    if not filtered_df.empty and filtered_df[metric_col].notna().any():
        avg_val = float(filtered_df[metric_col].mean())
        suffix = " pts" if score_display_mode == "Raw Points Earned" else "%"
        st.metric(metric_label, f"{round(avg_val, 1)}{suffix}")
    else:
        st.metric(metric_label, "N/A")

# Interactive Chart
st.subheader(f"Score Progress Over Weeks ({score_display_mode})")
if not filtered_df.empty:
    fig = px.line(
        filtered_df,
        x="Week",
        y=metric_col,
        color="Celebrity",
        markers=True,
        title=f"Weekly Performance Progression ({score_display_mode})",
    )
    fig.update_xaxes(type="linear")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Please select at least one celebrity from the sidebar.")

# Raw Data Table
st.subheader("Raw Performance Data")
st.dataframe(filtered_df[["Season", "Week", "Celebrity", "Score", "Max_Score", "Percentage"]])