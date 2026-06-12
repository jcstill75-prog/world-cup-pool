import streamlit as st
import pandas as pd

st.set_page_config(page_title="Office World Cup Pool", page_icon="⚽", layout="wide")

st.title("🏆 Office World Cup Sweepstakes Leaderboard")
st.markdown("Track your assigned teams' performance. Rankings update instantly as match results are logged.")

# --- NEW: SCORING RULES SECTION ---
with st.expander("📖 How does the scoring work? (Click to expand)"):
    st.markdown("""
    **Base Match Stats (Applies to all games)**
    * **Goals Scored:** 1 point per goal
    * **Clean Sheet:** 2 points (awarded if a team allows exactly 0 goals)

    **Group Stage Outcomes**
    * **Match Win:** 3 points
    * **Match Draw:** 1 point

    **Knockout Stage Advancements (Single Elimination)**
    * **Winning in the Round of 16:** 10 points
    * **Winning in the Quarter-Finals:** 15 points
    * **Winning in the Semi-Finals:** 20 points
    * **Winning the 3rd Place Match:** 10 points
    * **Winning the Final (World Cup Champions):** 25 points
    """)
# -----------------------------------

# Load Data Safely
@st.cache_data(ttl=60)  
def load_data():
    try:
        colleagues_df = pd.read_csv("colleagues.csv")
        matches_df = pd.read_csv("matches.csv")
        return colleagues_df, matches_df
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return None, None

colleagues, matches = load_data()

if colleagues is not None and matches is not None:
    # Get all unique teams across the three tiers
    all_teams = pd.concat([colleagues['Tier_1'], colleagues['Tier_2'], colleagues['Tier_3']]).dropna().unique()
    
    team_stats = {team: {"Points": 0, "Wins": 0, "Draws": 0, "Goals For": 0, "Clean Sheets": 0} for team in all_teams}

    # Process Matches & Calculate Points for Teams
    for _, row in matches.dropna(subset=['Team_1', 'Team_2']).iterrows():
        t1, t2 = row['Team_1'].strip(), row['Team_2'].strip()
        s1, s2 = int(row['Team_1_Score']), int(row['Team_2_Score'])
        stage = row['Stage']
        
        if t1 not in team_stats: team_stats[t1] = {"Points": 0, "Wins": 0, "Draws": 0, "Goals For": 0, "Clean Sheets": 0}
        if t2 not in team_stats: team_stats[t2] = {"Points": 0, "Wins": 0, "Draws": 0, "Goals For": 0, "Clean Sheets": 0}
        
        # Goals For Points
        team_stats[t1]["Goals For"] += s1
        team_stats[t1]["Points"] += s1
        team_stats[t2]["Goals For"] += s2
        team_stats[t2]["Points"] += s2
        
        # Clean Sheet Points
        if s2 == 0:
            team_stats[t1]["Clean Sheets"] += 1
            team_stats[t1]["Points"] += 2
        if s1 == 0:
            team_stats[t2]["Clean Sheets"] += 1
            team_stats[t2]["Points"] += 2
            
        # Match Outcome Points
        if s1 > s2:
            team_stats[t1]["Wins"] += 1
            if stage == "Group":
                team_stats[t1]["Points"] += 3
            else:
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

    # Map stats back to Colleagues (Summing their 3 teams)
    leaderboard_data = []
    for _, row in colleagues.iterrows():
        name = row['Colleague']
        t1, t2, t3 = str(row['Tier_1']).strip(), str(row['Tier_2']).strip(), str(row['Tier_3']).strip()
        
        total_points = 0
        total_wins = 0
        total_draws = 0
        total_goals = 0
        total_cleansheets = 0
        
        for t in [t1, t2, t3]:
            if t != 'nan' and t in team_stats:
                total_points += team_stats[t]["Points"]
                total_wins += team_stats[t]["Wins"]
                total_draws += team_stats[t]["Draws"]
                total_goals += team_stats[t]["Goals For"]
                total_cleansheets += team_stats[t]["Clean Sheets"]

        teams_string = f"{t1}, {t2}, {t3}"
        
        leaderboard_data.append({
            "Rank": 0,
            "Player": name,
            "Assigned Teams": teams_string,
            "Total Points": total_points,
            "Match Wins": total_wins,
            "Match Draws": total_draws,
            "Goals Scored": total_goals,
            "Clean Sheets": total_cleansheets
        })
        
    leaderboard_df = pd.DataFrame(leaderboard_data)
    leaderboard_df = leaderboard_df.sort_values(by=["Total Points", "Match Wins", "Goals Scored"], ascending=False).reset_index(drop=True)
    leaderboard_df["Rank"] = leaderboard_df.index + 1

    # Display Dashboard
    st.subheader("🔥 Current Standings")
    st.dataframe(
        leaderboard_df, 
        hide_index=True,
        use_container_width=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "Total Points": st.column_config.NumberColumn("Total Points", help="Combined score of all 3 assigned teams")
        }
    )
        
    st.subheader("🏃 Played Matches Log")
    st.dataframe(matches, hide_index=True, use_container_width=True)
        
    st.info("💡 **Admin Tip:** To update standings or log a new match, simply edit the `matches.csv` file in your GitHub repository. The dashboard refreshes automatically.")
