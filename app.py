import pandas as pd
import plotly.express as px
import streamlit as st

# Set up the Streamlit page layout and title
st.set_page_config(page_title="DWTS Analytics Dashboard", layout="wide")
st.title("💃 Dancing with the Stars Dashboard")

# Load the CSV file using the numpy_nullable backend for robust data handling
df = pd.read_csv("dwts_data.csv", dtype_backend="numpy_nullable")

# Strip leading and trailing whitespaces from column headers
df.columns = df.columns.str.strip()

# Automatically map various possible CSV column names to standard app names
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

# Apply the mapping to rename columns
df = df.rename(columns=column_mapping)

# Remove any duplicate columns if multiple matches occurred
df = df.loc[:, ~df.columns.duplicated()]

# Verify that all mandatory columns exist in the dataset
required_cols = ["Celebrity", "Week", "Score"]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"Missing required columns: {missing}. Found columns in your CSV: {list(df.columns)}")
    st.stop()

# Safety check: ensure 'Celebrity' is a single column series, not a dataframe
if isinstance(df["Celebrity"], pd.DataFrame):
    df["Celebrity"] = df["Celebrity"].iloc[:, 0]

# Parse scores and fractions, and assign max possible scores (Weeks 4 and 6 are out of 40; others out of 30)
earned_scores = []
max_scores = []

for idx, row in df.iterrows():
    val_str = str(row["Score"]).strip()
    week_val = row.get("Week", None)
    
    earned = None
    possible = None
    
    # Check if the score entry contains a slash
    if "/" in val_str:
        parts = [p.strip() for p in val_str.split("/") if p.strip() != ""]
        if len(parts) >= 2:
            earned = pd.to_numeric(parts[0], errors="coerce")
            possible = pd.to_numeric(parts[1], errors="coerce")
        elif len(parts) == 1:
            earned = pd.to_numeric(parts[0], errors="coerce")
    else:
        earned = pd.to_numeric(val_str, errors="coerce")
        
    # Default max score logic if not explicitly defined in a fraction
    if pd.isna(possible):
        if str(week_val) in ["4", "6"]:
            possible = 40
        else:
            possible = 30
            
    earned_scores.append(earned)
    max_scores.append(possible)

# Assign cleaned numeric values back to the DataFrame
df["Score"] = pd.Series(earned_scores, dtype="float64")
df["Max_Score"] = pd.Series(max_scores, dtype="float64")
df["Percentage"] = (df["Score"] / df["Max_Score"]) * 100
df["Week"] = pd.to_numeric(df["Week"], errors="coerce")

# Set up sidebar controls for filtering and display preferences
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

# Filter the DataFrame based on user selections and sort by week order
filtered_df = df[df["Celebrity"].isin(selected_celebrity)].sort_values(by="Week")

# Determine which column and label to use based on the sidebar toggle
metric_col = "Score" if score_display_mode == "Raw Points Earned" else "Percentage"
metric_label = "Average Score (Points)" if score_display_mode == "Raw Points Earned" else "Average Performance (%)"

# Display summary metrics at the top of the dashboard
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

# Calculate overall rankings sorted by Total Points
st.subheader("🏆 Leaderboard & Rankings (by Total Points)")

if not filtered_df.empty:
    # Group by Celebrity and compute total points, total dances, average performance, and average points
    leaderboard = (
        filtered_df.groupby("Celebrity")
        .agg(
            Total_Points=("Score", "sum"),
            Dances_Count=("Week", "count"),
            Avg_Percentage=("Percentage", "mean"),
            Avg_Points=("Score", "mean"),
        )
        .reset_index()
    )

    # Sort by Total Points descending
    leaderboard = leaderboard.sort_values(by="Total_Points", ascending=False)
    
    # Add Rank column (1, 2, 3...) based on total points accumulated
    leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))
    
    # Format numbers for cleaner presentation
    leaderboard["Avg_Percentage"] = leaderboard["Avg_Percentage"].round(1).astype(str) + "%"
    leaderboard["Avg_Points"] = leaderboard["Avg_Points"].round(1)

    # Rename columns for table display
    leaderboard = leaderboard.rename(columns={
        "Total_Points": "Total Points Earned",
        "Dances_Count": "Dances Tracked",
        "Avg_Percentage": "Avg Performance (%)",
        "Avg_Points": "Avg Score (pts)"
    })

    st.dataframe(leaderboard, use_container_width=True, hide_index=True)
else:
    st.write("No celebrity data to display for rankings.")

# Render the interactive line chart visualization
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

# Display the underlying raw data table
st.subheader("Raw Performance Data")
st.dataframe(filtered_df[["Season", "Week", "Celebrity", "Score", "Max_Score", "Percentage"]])
