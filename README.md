# Dancing with the Stars Analytics Dashboard (Season 35)

## Overview
Evaluating multi-week competition metrics presents unique data normalization challenges due to shifting judge panel capacities, fractional score entries, and variable weekly maximum score caps. This repository implements an interactive analytics dashboard that ingests raw weekly performance logs and normalizes contestant scoring trajectories over time.

## How It Works
The app reads scoring data from a spreadsheet and automatically processes it:

1. **Clean Column Names:** Automatically fixes small formatting errors or extra spaces in spreadsheet column headers.
2. **Fractional Score Support:** Reads fractional scores (like `18/30` or `34/40`) and converts them into accurate percentage scores for fair comparisons across different weeks.
3. **Total Points Leaderboard:** Adds up total points across all weeks to display an updated contestant ranking.
4. **Interactive Graphs:** Uses Plotly to build line charts so users can easily select and compare how different contestants perform week by week.

## Repository Structure & Data Format
- `app.py` — The main Python script that powers the dashboard logic and visual layout.
- `dwts_data.csv` — The spreadsheet file holding contestant names, weeks, dance styles, and scores.

### Data Format Example
The CSV file (`dwts_data.csv`) contains the following structured columns:
- **Season:** Season number (e.g., `35`).
- **Week:** Week number of the competition.
- **Celebrity:** Name of the celebrity contestant.
- **Partner:** Professional dance partner.
- **Dance:** Style of dance performed.
- **Score:** Score earned for the week (supports fractional scores like `18/30` or `34/40`).
- **Eliminated:** Elimination or jeopardy status (`Yes` or `No`).

```text
Season   Week   Celebrity        Partner             Dance      Score   Eliminated
35       1      Amber Glenn      Pasha Pashkov       cha cha    18/30   No
35       1      Ciara Miller     Brandon Armstrong   foxtrot    15/30   No
35       1      Conner Leavitt   Adele Zaikman       Salsa      12/30   Yes
35       1      Connor Wood      Rylee Arnold        cha cha    16/30   No
```
## Future Works & Coming Soon
- **Predictive Elimination Modeling:** Integrating machine learning classifiers to forecast upcoming contestant eliminations based on historical score trends.
- **Advanced Sentiment Analytics:** Analyzing weekly social media engagement metrics alongside judge scores to measure public popularity impact.

## How to Run
This app is built using Python and Streamlit. Running `app.py` loads the data from `dwts_data.csv` and launches the interactive dashboard directly in a web browser.

## References
1. [Streamlit Documentation](https://docs.streamlit.io/)
2. [Plotly Express Python Library](https://plotly.com/python/plotly-express/)
3. [Pandas User Guide](https://pandas.pydata.org/docs/user_guide/index.html)
