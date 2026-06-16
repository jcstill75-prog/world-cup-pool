import streamlit as st
import pandas as pd

st.set_page_config(page_title="Office World Cup Pool", page_icon="⚽", layout="wide")

st.title("🏆 Office World Cup Sweepstakes Leaderboard")
st.markdown("Track your randomly assigned team's performance. Rankings update instantly as match results are logged.")

# ---------------------------------------------------------
# 1. EXPLANATION OF SCORING
# ---------------------------------------------------------
st.subheader("📋 How Scoring Works")
st.markdown("""
- **Match Win (Group Stage):** 3 points
- **Match Draw (Group Stage):** 1 point
- **Goals Scored:** 1 point per goal
- **Clean Sheet:** 2 bonus points
- **Knockout Stage Advancements:** Massive bonus points for surviving! (Round of 16: +10pts, Quarter-Finals: +15pts, Semi-Finals: +20pts, Final: +25pts)
""")

st.divider()

# Load Data Safely
@st.cache_data(ttl=60)  # Refresh data every 60 seconds
def load_data():
    try:
        colleagues_df = pd.read_csv("colleagues.csv")
        
        # BULLETPROOF HEADER FIX: Strips invisible spaces and fixes capitalization
        colleagues_df.columns = colleagues_df.columns.str.strip().str.title()
        
        # Automatically renames common variations so the code never crashes
        colleagues_df = colleagues_df.rename(columns={
            "Player": "Colleague", 
            "Name": "Colleague",
            "Country": "Team",
            "Assigned Team": "Team",
            "Tier 1: Favourite": "Team",
            "Tier 1": "Team"
        })
        
        # Stream live data from your public Google Sheet
        sheet_url = "https://docs.google.com/spreadsheets/d/1AcO04Psm2XkvEWB8KtSR8ux-20SmVeSF_AxnYp2Vkls/edit?usp=sharing"
        csv_url = sheet_url.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv")
        matches_df = pd.read_csv(csv_url)
        
        return colleagues_df, matches_df
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return None, None

colleagues, matches = load_data()

if colleagues is not None and matches is not None:
    # Initialize points dictionary for teams
    team_stats = {team: {"Points": 0, "Wins": 0, "Draws": 0, "Goals For": 0, "Clean Sheets": 0} 
                  for team in colleagues["Team"].unique()}

    # Process Matches & Calculate Points
    for _, row in matches.dropna(subset=['Team_1', 'Team_2']).iterrows():
        t1, t2 = str(row['Team_1']).strip(), str(row['Team_2']).strip()
        
        # Ensure scores are integers; skip blank/unplayed games
        try:
            s1, s2 = int(row['Team_1_Score']), int(row['Team_2_Score'])
        except (ValueError, TypeError):
            continue
            
        stage = str(row['Stage']).strip()
        
        # Ensure teams exist in our tracking
        if t1 not in team_stats: team_stats[t1] = {"Points": 0, "Wins": 0, "Draws": 0, "Goals For": 0, "Clean Sheets": 0}
        if t2 not in team_stats: team_stats[t2] = {"Points": 0, "Wins": 0, "Draws": 0, "Goals For": 0, "Clean Sheets": 0}
        
        # 1. Goals For Points (1 pt per goal)
        team_stats[t1]["Goals For"] += s1
        team_stats[t1]["Points"] += s1
        team_stats[t2]["Goals For"] += s2
        team_stats[t2]["Points"] += s2
        
        # 2. Clean Sheet Points (2 pts)
        if s2 == 0:
            team_stats[t1]["Clean Sheets"] += 1
            team_stats[t1]["Points"] += 2
        if s1 == 0:
            team_stats[t2]["Clean Sheets"] += 1
            team_stats[t2]["Points"] += 2
            
        # 3. Match Outcome Points
        if s1 > s2:
            team_stats[t1]["Wins"] += 1
            if stage == "Group":
                team_stats[t1]["Points"] += 3  # Group Win
            else:
                # Knockout Advancement Bonuses
                if stage == "Round of 16": team_stats[t1]["Points"] += 10
                elif stage == "Quarter-Finals": team_stats[t1]["Points"] += 15
                elif stage == "Semi-Finals": team_stats[t1]["Points"] += 20
                elif stage == "3rd Place Match": team_stats[t1]["Points"] += 10
                elif stage == "Final": team_stats[t1]["Points"] += 25
        elif s2 > s1:
            team_stats[t2]["Wins"] += 1
            if stage == "Group":
                team_stats[t2]["Points"] += 3
            else:
                if stage == "Round of 16": team_stats[t2]["Points"] += 10
                elif stage == "Quarter-Finals": team_stats[t2]["Points"] += 15
                elif stage == "Semi-Finals": team_stats[t2]["Points"] += 20
                elif stage == "3rd Place Match": team_stats[t2]["Points"] += 10
                elif stage == "Final": team_stats[t2]["Points"] += 25
        else:
            if stage == "Group":
                team_stats[t1]["Draws"] += 1
                team_stats[t2]["Draws"] += 1
                team_stats[t1]["Points"] += 1
                team_stats[t2]["Points"] += 1

    # Map stats back to Colleagues
    leaderboard_data = []
    for _, row in colleagues.iterrows():
        name = row['Colleague']
        team = row['Team']
        stats = team_stats.get(team, {"Points": 0, "Wins": 0, "Draws": 0, "Goals For": 0, "Clean Sheets": 0})
        leaderboard_data.append({
            "Rank": 0,
            "Colleague": name,
            "Assigned Team": team,
            "Total Points": stats["Points"],
            "Match Wins": stats["Wins"],
            "Match Draws": stats["Draws"],
            "Goals Scored": stats["Goals For"],
            "Clean Sheets": stats["Clean Sheets"]
        })
        
    leaderboard_df = pd.DataFrame(leaderboard_data)
    # Sort by points, then wins, then goals scored
    leaderboard_df = leaderboard_df.sort_values(by=["Total Points", "Match Wins", "Goals Scored"], ascending=False).reset_index(drop=True)
    leaderboard_df["Rank"] = leaderboard_df.index + 1

    # ---------------------------------------------------------
    # 2. LEADERBOARD (Full Width)
    # ---------------------------------------------------------
    st.subheader("🔥 Current Standings")
    st.dataframe(
        leaderboard_df, 
        hide_index=True,
        use_container_width=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "Total Points": st.column_config.NumberColumn("Total Points", help="Calculated using custom sweepstakes rules")
        }
    )
    
    st.divider()

    # ---------------------------------------------------------
    # 3. MATCH LOG (Full Width)
    # ---------------------------------------------------------
    st.subheader("🏃 Played Matches Log")
    st.dataframe(matches, hide_index=True, use_container_width=True)
        
    st.info("💡 **Admin Tip:** To update standings or log a new match, simply add the score to your Google Sheet. The dashboard refreshes automatically within 60 seconds.")