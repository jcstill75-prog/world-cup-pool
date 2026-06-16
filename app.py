import streamlit as st
import pandas as pd
import datetime

# Set premium page layout
st.set_page_config(
    page_title="World Cup 2026 Office Pool",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title & Styling Customization
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; }
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 World Cup 2026 Office Pool Dashboard")
st.markdown("Track your office draft standings live! Connected directly to your Google Sheet.")

# ----------------- SIDEBAR CONFIGURATION -----------------
st.sidebar.header("⚙️ Dashboard Settings")

# Google Sheet Configuration Input
default_url = "https://docs.google.com/spreadsheets/d/YOUR_ACTUAL_SHEET_LINK_HERE/edit?usp=sharing"
sheet_url = st.sidebar.text_input(
    "https://docs.google.com/spreadsheets/d/1AcO04Psm2XkvEWB8KtSR8ux-20SmVeSF_AxnYp2Vkls/edit?usp=sharing",
    value=default_url,
    help="Make sure the Google Sheet access is set to 'Anyone with the link can view'."
)

st.sidebar.markdown("---")
st.sidebar.subheader("💡 Point Calculation Rules")
st.sidebar.markdown("""
- **Match Win:** 3 points
- **Match Draw:** 1 point
- **Goals Scored:** 1 point per goal
- **Clean Sheet:** 2 bonus points
""")

# ----------------- DATA LOADING ENGINE -----------------
@st.cache_data(ttl="5m")  # Caches for only 5 minutes, giving you ultra-fresh data
def load_data(url):
    # 1. Load Draft Pool (colleagues.csv) with robust header handling
    try:
        colleagues_df = pd.read_csv("colleagues.csv")
        # Normalize column names to lowercase to prevent capitalization mismatches
        colleagues_df.columns = [c.strip().lower() for c in colleagues_df.columns]
        
        # Standardize column mappings
        rename_map = {}
        for col in colleagues_df.columns:
            if col in ['colleague', 'player', 'name', 'participant', 'user']:
                rename_map[col] = 'Colleague'
            elif col in ['team', 'country', 'selection', 'draft']:
                rename_map[col] = 'Team'
        colleagues_df = colleagues_df.rename(columns=rename_map)
        
        # Ensure required columns exist
        if 'Colleague' not in colleagues_df.columns or 'Team' not in colleagues_df.columns:
            st.sidebar.warning("⚠️ 'colleagues.csv' is missing standard columns. Using mock draft.")
            raise ValueError("Invalid headers")
            
    except Exception:
        # Graceful fallback mock dataset so the app never shows a red error screen
        colleagues_df = pd.DataFrame([
            {"Colleague": "Sarah", "Team": "Germany"},
            {"Colleague": "Sarah", "Team": "Australia"},
            {"Colleague": "Sarah", "Team": "Spain"},
            {"Colleague": "Mike", "Team": "Sweden"},
            {"Colleague": "Mike", "Team": "USA"},
            {"Colleague": "Mike", "Team": "Canada"},
            {"Colleague": "Dave", "Team": "Mexico"},
            {"Colleague": "Dave", "Team": "Ivory Coast"},
            {"Colleague": "Dave", "Team": "Netherlands"},
            {"Colleague": "Jenny", "Team": "Korea Republic"},
            {"Colleague": "Jenny", "Team": "Belgium"},
            {"Colleague": "Jenny", "Team": "Brazil"}
        ])
    
    # Clean draft team names
    colleagues_df['Team'] = colleagues_df['Team'].astype(str).str.strip()

    # 2. Parse Google Sheet URL to live CSV download stream
    if "YOUR_ACTUAL_SHEET_LINK_HERE" in url or not url.startswith("https://"):
        # Dummy matches to prevent crash prior to user adding their link
        mock_matches = pd.DataFrame([
            {"Stage": "Group", "Team_1": "Mexico", "Team_1_Score": 2, "Team_2": "South Africa", "Team_2_Score": 0},
            {"Stage": "Group", "Team_1": "Sweden", "Team_1_Score": 5, "Team_2": "Tunisia", "Team_2_Score": 1}
        ])
        return colleagues_df, mock_matches, True

    try:
        csv_url = url.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv")
        csv_url = csv_url.split("/edit")[0] + "/gviz/tq?tqx=out:csv" # robust fallback regex split
        matches_df = pd.read_csv(csv_url)
        
        # Verify columns match expected structure
        expected = ['Stage', 'Team_1', 'Team_1_Score', 'Team_2', 'Team_2_Score']
        matches_df.columns = [c.strip() for c in matches_df.columns]
        
        # Keep only required columns and drop completely empty rows
        matches_df = matches_df[expected].dropna(subset=['Team_1', 'Team_2'])
        return colleagues_df, matches_df, False
    except Exception as e:
        st.error(f"Failed to fetch live Google Sheet: {e}. Displaying offline backup.")
        # Fallback empty structure
        empty_matches = pd.DataFrame(columns=['Stage', 'Team_1', 'Team_1_Score', 'Team_2', 'Team_2_Score'])
        return colleagues_df, empty_matches, True

# Load our datasets
colleagues, matches, is_using_fallback = load_data(sheet_url)

# Manual Cache Clear Button
if st.sidebar.button("🔄 Force Clear Cache & Refresh"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(f"Last fetched: {datetime.datetime.now().strftime('%H:%M:%S')}")

if is_using_fallback:
    st.info("ℹ️ App is currently running on mock or default backup data. Replace the Google Sheet link in the sidebar to stream your live pool!")

# ----------------- STANDINGS & POINTS CALCULATOR -----------------
# We calculate scores dynamically from the match logs
team_records = {}

for _, row in matches.iterrows():
    t1 = str(row['Team_1']).strip()
    t2 = str(row['Team_2']).strip()
    
    # Ensure scores are integers
    try:
        s1 = int(row['Team_1_Score'])
        s2 = int(row['Team_2_Score'])
    except (ValueError, TypeError):
        continue  # Skip unplayed matches
    
    # Initialize team tracking if not yet registered
    for team in [t1, t2]:
        if team not in team_records:
            team_records[team] = {
                "Wins": 0, "Draws": 0, "Losses": 0, 
                "Goals_Scored": 0, "Clean_Sheets": 0, "Match_Points": 0
            }
            
    # Track Goals Scored
    team_records[t1]["Goals_Scored"] += s1
    team_records[t2]["Goals_Scored"] += s2
    
    # Check for Clean Sheets
    if s2 == 0:
        team_records[t1]["Clean_Sheets"] += 1
    if s1 == 0:
        team_records[t2]["Clean_Sheets"] += 1
        
    # Match Outcome Calculations
    if s1 > s2:
        team_records[t1]["Wins"] += 1
        team_records[t1]["Match_Points"] += 3
        team_records[t2]["Losses"] += 1
    elif s2 > s1:
        team_records[t2]["Wins"] += 1
        team_records[t2]["Match_Points"] += 3
        team_records[t1]["Losses"] += 1
    else:
        team_records[t1]["Draws"] += 1
        team_records[t1]["Match_Points"] += 1
        team_records[t2]["Draws"] += 1
        team_records[t2]["Match_Points"] += 1

# Map Team Stats back to Table
team_data_list = []
for team, stats in team_records.items():
    # Calculate Total Pool Points for each country:
    # Match Points (Wins/Draws) + Goals Scored (1pt each) + Clean Sheet bonus (2pts each)
    total_pts = stats["Match_Points"] + stats["Goals_Scored"] + (stats["Clean_Sheets"] * 2)
    team_data_list.append({
        "Team": team,
        "Wins": stats["Wins"],
        "Draws": stats["Draws"],
        "Losses": stats["Losses"],
        "Goals Scored": stats["Goals_Scored"],
        "Clean Sheets": stats["Clean_Sheets"],
        "Total Points": total_pts
    })

teams_df = pd.DataFrame(team_data_list)

# If no matches are recorded yet, build empty structure
if teams_df.empty:
    teams_df = pd.DataFrame(columns=["Team", "Wins", "Draws", "Losses", "Goals Scored", "Clean Sheets", "Total Points"])

# ----------------- CALCULATE PLAYER LEADERBOARD -----------------
# Merge colleague picks with team results
leaderboard_list = []
grouped_colleagues = colleagues.groupby("Colleague")

for participant, group in grouped_colleagues:
    drafted_teams = group["Team"].tolist()
    
    p_wins, p_draws, p_goals, p_clean_sheets, p_total = 0, 0, 0, 0, 0
    detailed_teams_progress = []
    
    for team in drafted_teams:
        if team in teams_df["Team"].values:
            t_row = teams_df[teams_df["Team"] == team].iloc[0]
            p_wins += t_row["Wins"]
            p_draws += t_row["Draws"]
            p_goals += t_row["Goals Scored"]
            p_clean_sheets += t_row["Clean Sheets"]
            p_total += t_row["Total Points"]
            detailed_teams_progress.append(f"{team} ({t_row['Total Points']} pts)")
        else:
            detailed_teams_progress.append(f"{team} (0 pts)")
            
    leaderboard_list.append({
        "Leaderboard Rank": 1, # Placeholder, calculated next
        "Colleague": participant,
        "Drafted Squad": ", ".join(detailed_teams_progress),
        "Wins Contribution": p_wins,
        "Draws Contribution": p_draws,
        "Goals Scored": p_goals,
        "Clean Sheets": p_clean_sheets,
        "Total Pool Points": p_total
    })

leaderboard_df = pd.DataFrame(leaderboard_list)

if not leaderboard_df.empty:
    # Rank players descending based on Total Pool Points, tie break on Wins, then Goals Scored
    leaderboard_df = leaderboard_df.sort_values(
        by=["Total Pool Points", "Wins Contribution", "Goals Scored"], 
        ascending=False
    ).reset_index(drop=True)
    leaderboard_df["Leaderboard Rank"] = leaderboard_df.index + 1
else:
    leaderboard_df = pd.DataFrame(columns=["Leaderboard Rank", "Colleague", "Drafted Squad", "Total Pool Points"])

# ----------------- METRIC CARDS OVERVIEW -----------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Matches Played", len(matches))
with col2:
    if not leaderboard_df.empty:
        top_player = leaderboard_df.iloc[0]["Colleague"]
        top_score = leaderboard_df.iloc[0]["Total Pool Points"]
        st.metric("Current Leader", f"{top_player}", f"{top_score} pts")
    else:
        st.metric("Current Leader", "None", "0 pts")
with col3:
    if not teams_df.empty:
        high_scoring_team = teams_df.sort_values(by="Goals Scored", ascending=False).iloc[0]["Team"]
        high_score = teams_df.sort_values(by="Goals Scored", ascending=False).iloc[0]["Goals Scored"]
        st.metric("Top Team Scorer", f"{high_scoring_team}", f"{high_score} goals")
    else:
        st.metric("Top Team Scorer", "N/A")
with col4:
    total_goals_scored = teams_df["Goals Scored"].sum() // 2 if not teams_df.empty else 0
    st.metric("Total Tournament Goals", f"{total_goals_scored}")

st.markdown("---")

# ----------------- TABS SYSTEM -----------------
tab1, tab2, tab3 = st.tabs(["🏆 Leaderboard Standings", "⚽ Live Match Logs", "📊 Team Performance Metrics"])

with tab1:
    st.subheader("Leaderboard Standings")
    st.dataframe(
        leaderboard_df.set_index("Leaderboard Rank"), 
        use_container_width=True
    )
    
    # Graphic visualization of standings
    if not leaderboard_df.empty:
        st.subheader("Standings Visualizer")
        chart_data = leaderboard_df.set_index("Colleague")[["Total Pool Points"]]
        st.bar_chart(chart_data, color="#2E86C1")

with tab2:
    st.subheader("Match Log History (Google Sheets Feed)")
    if matches.empty:
        st.write("No matches played yet.")
    else:
        st.dataframe(matches, use_container_width=True, height=400)

with tab3:
    st.subheader("Team-by-Team Contribution Breakdowns")
    if teams_df.empty:
        st.write("No team statistics calculated yet.")
    else:
        st.dataframe(
            teams_df.sort_values(by="Total Points", ascending=False).reset_index(drop=True), 
            use_container_width=True
        )
