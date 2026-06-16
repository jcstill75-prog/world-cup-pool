import streamlit as st
import pandas as pd

st.set_page_config(page_title="Office World Cup Pool", page_icon="⚽", layout="wide")

st.title("🏆 Office World Cup Sweepstakes Leaderboard")
st.markdown("Track your assigned teams' performance. Rankings update instantly as match results are logged.")

# --- SCORING RULES SECTION ---
with st.expander("📖 How does the scoring work? (Click to expand)"):
    st.markdown("""
    **Base Match Stats (Applies to all games)**
    * **Goals Scored:** 1 point per goal
    * **Clean Sheet:** 2 points (awarded if a team allows exactly 0 goals)

    **Group Stage Outcomes**
    * **Match Win:** 3 points
    * **Match Draw:** 1 point

    **The Giant Killer Bonus**
    * **Massive Upset:** 5 bonus points awarded if a team defeats an opponent ranked 25 or more spots higher than them in the pre-tournament FIFA rankings.

    **Knockout Stage Advancements (Single Elimination)**
    * **Winning in the Round of 16:** 10 points
    * **Winning in the Quarter-Finals:** 15 points
    * **Winning in the Semi-Finals:** 20 points
    * **Winning the 3rd Place Match:** 10 points
    * **Winning the Final (World Cup Champions):** 25 points
    """)
# -----------------------------------

# Static FIFA Rankings for the 2026 Pool Teams
fifa_rankings = {
    "Argentina": 1, "France": 2, "Belgium": 3, "England": 4, "Brazil": 5,
    "Portugal": 6, "Netherlands": 7, "Spain": 8, "Croatia": 10, "USA": 11,
    "Colombia": 12, "Morocco": 13, "Mexico": 14, "Uruguay": 15, "Germany": 16,
    "Senegal": 17, "Japan": 18, "Switzerland": 19, "Iran": 20, "Korea Republic": 23,
    "Australia": 24, "Austria": 25, "Sweden": 26, "Tunisia": 28, "Qatar": 34,
    "Türkiye": 35, "Egypt": 36, "Côte D'Ivoire": 38, "Scotland": 39, "Czechia": 40,
    "Algeria": 43, "Ecuador": 43, "Norway": 44, "Panama": 45, "Canada": 49,
    "Saudi Arabia": 53, "Paraguay": 56, "South Africa": 58, "Iraq": 58, "Ghana": 61,
    "Congo DR": 63, "Uzbekistan": 64, "Cabo Verde": 65, "Jordan": 70, 
    "Bosnia & Herzegovina": 74, "Haiti": 90, "Curaçao": 91, "New Zealand": 104
}

# Load Data Safely
@st.cache_data(ttl="10m")  
def load_data():
    try:
        colleagues_df = pd.read_csv("colleagues.csv")
        matches_df = pd.read_csv("https://raw.githubusercontent.com/jcstill75-prog/world-cup-pool/refs/heads/main/matches.csv?token=GHSAT0AAAAAAD72F4R6BV7XJMNPYMTSFOLA2RRKZUQ")
        return colleagues_df, matches_df
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return None, None

colleagues, matches = load_data()

if colleagues is not None and matches is not None:
    # Get all unique teams across the three tiers
    all_teams = pd.concat([colleagues['Tier_1'], colleagues['Tier_2'], colleagues['Tier_3']]).dropna().unique()
    
    # Include Bonus tracking in stats
    team_stats = {team: {"Points": 0, "Wins": 0, "Draws": 0, "Goals For": 0, "Clean Sheets": 0, "Bonuses": 0} for team in all_teams}

    # Process Matches & Calculate Points for Teams
    for _, row in matches.dropna(subset=['Team_1', 'Team_2']).iterrows():
        t1, t2 = row['Team_1'].strip(), row['Team_2'].strip()
        s1, s2 = int(row['Team_1_Score']), int(row['Team_2_Score'])
        stage = row['Stage']
        
        if t1 not in team_stats: team_stats[t1] = {"Points": 0, "Wins": 0, "Draws": 0, "Goals For": 0, "Clean Sheets": 0, "Bonuses": 0}
        if t2 not in team_stats: team_stats[t2] = {"Points": 0, "Wins": 0, "Draws": 0, "Goals For": 0, "Clean Sheets": 0, "Bonuses": 0}
        
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
            
        # Match Outcome & Giant Killer Points
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
            
            # Giant Killer Check (Team 1 wins)
            # A higher numerical rank means a "worse" team. So if t1 is rank 50 and t2 is rank 10: 50 - 10 = 40. 40 >= 25 triggers bonus.
            rank1 = fifa_rankings.get(t1, 50)
            rank2 = fifa_rankings.get(t2, 50)
            if rank1 - rank2 >= 25:
                team_stats[t1]["Points"] += 5
                team_stats[t1]["Bonuses"] += 1

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
                
            # Giant Killer Check (Team 2 wins)
            rank1 = fifa_rankings.get(t1, 50)
            rank2 = fifa_rankings.get(t2, 50)
            if rank2 - rank1 >= 25:
                team_stats[t2]["Points"] += 5
                team_stats[t2]["Bonuses"] += 1
                
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
        total_bonuses = 0
        
        for t in [t1, t2, t3]:
            if t != 'nan' and t in team_stats:
                total_points += team_stats[t]["Points"]
                total_wins += team_stats[t]["Wins"]
                total_draws += team_stats[t]["Draws"]
                total_goals += team_stats[t]["Goals For"]
                total_cleansheets += team_stats[t]["Clean Sheets"]
                total_bonuses += team_stats[t]["Bonuses"]

        teams_string = f"{t1}, {t2}, {t3}"
        
        leaderboard_data.append({
            "Rank": 0,
            "Player": name,
            "Assigned Teams": teams_string,
            "Total Points": total_points,
            "Giant Killer Bonuses": total_bonuses,
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
            "Total Points": st.column_config.NumberColumn("Total Points", help="Combined score of all 3 assigned teams"),
            "Giant Killer Bonuses": st.column_config.NumberColumn("Giant Killer Bonuses", help="Number of times an assigned team triggered the 5-point upset bonus")
        }
    )
        
    st.subheader("🏃 Played Matches Log")
    st.dataframe(matches, hide_index=True, use_container_width=True)
        
    st.info("💡 **Admin Tip:** To update standings or log a new match, simply edit the `matches.csv` file in your GitHub repository. The dashboard refreshes automatically.")
