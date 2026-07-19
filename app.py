import streamlit as st
import pandas as pd

st.set_page_config(page_title="Office World Cup Pool", page_icon="⚽", layout="wide")

st.title("🏆 Office World Cup Sweepstakes Leaderboard")
st.markdown("Track your assigned teams' performance. Rankings update instantly as match results are logged.")

# ---------------------------------------------------------
# 1. EXPLANATION OF SCORING
# ---------------------------------------------------------
st.subheader("📋 How Scoring Works")
st.markdown("""
- **Match Win (Group):** 3 points
- **Match Draw (Group):** 1 point
- **Goals Scored:** 1 point per goal
- **Clean Sheet:** 2 bonus points
- **Knockout Stage Advancements:** Massive bonus points replacing the standard win! (Round of 32: +5pts, Round of 16: +10pts, Quarter-Finals: +15pts, Semi-Finals: +20pts, Final: +25pts, 3rd Place: +10pts)
""")
st.divider()

# ---------------------------------------------------------
# ELIMINATED TEAMS TRACKER
# ---------------------------------------------------------
# Updated as of July 7, 2026 (Quarter-Finals Set)
ELIMINATED_TEAMS = [
    "Algeria", "Australia", "Austria", "Bosnia & Herzegovina", "Brazil", 
    "Cabo Verde", "Canada", "Congo DR", "Côte D'Ivoire", "Croatia", 
    "Curaçao", "Czechia", "Ecuador", "Egypt", "Germany", "Ghana", 
    "Haiti", "Iran", "Iraq", "Japan", "Jordan", "Korea Republic", 
    "Mexico", "Netherlands", "New Zealand", "Panama", "Paraguay", 
    "Portugal", "Qatar", "Saudi Arabia", "Scotland", "Senegal", 
    "South Africa", "Sweden", "Tunisia", "Türkiye", "Uruguay", 
    "USA", "Uzbekistan", "Colombia", "Morocco", "Belgium", "Norway", "Switzerland", "France", "England", "Argentina"
]

# ---------------------------------------------------------
# HARDCODED DRAFT DATA
# ---------------------------------------------------------
@st.cache_data
def get_draft_data():
    return pd.DataFrame([
        {"Player": "Amanda", "Tier 1": "Germany", "Tier 2": "Canada", "Tier 3": "Panama"},
        {"Player": "Ana", "Tier 1": "Belgium", "Tier 2": "Norway", "Tier 3": "Qatar"},
        {"Player": "Brian", "Tier 1": "France", "Tier 2": "Australia", "Tier 3": "Jordan"},
        {"Player": "Cassie", "Tier 1": "Colombia", "Tier 2": "Egypt", "Tier 3": "Algeria"},
        {"Player": "Craig", "Tier 1": "Mexico", "Tier 2": "Korea Republic", "Tier 3": "South Africa"},
        {"Player": "Emma", "Tier 1": "USA", "Tier 2": "Japan", "Tier 3": "Uzbekistan"},
        {"Player": "Jasmine (& Rob)", "Tier 1": "England", "Tier 2": "Senegal", "Tier 3": "Bosnia & Herzegovina"},
        {"Player": "Jennifer", "Tier 1": "Brazil", "Tier 2": "Czechia", "Tier 3": "Cabo Verde"},
        {"Player": "Le'Otis", "Tier 1": "Switzerland", "Tier 2": "Türkiye", "Tier 3": "Haiti"},
        {"Player": "Linda", "Tier 1": "Croatia", "Tier 2": "Austria", "Tier 3": "Saudi Arabia"},
        {"Player": "Mark", "Tier 1": "Portugal", "Tier 2": "Ghana", "Tier 3": "Curaçao"},
        {"Player": "Rebecca", "Tier 1": "Netherlands", "Tier 2": "Scotland", "Tier 3": "Congo DR"},
        {"Player": "Ramon", "Tier 1": "Uruguay", "Tier 2": "Paraguay", "Tier 3": "Iran"},
        {"Player": "Stacie", "Tier 1": "Morocco", "Tier 2": "Sweden", "Tier 3": "New Zealand"},
        {"Player": "Taliah", "Tier 1": "Spain", "Tier 2": "Tunisia", "Tier 3": "Côte D'Ivoire"},
        {"Player": "Tressa", "Tier 1": "Argentina", "Tier 2": "Ecuador", "Tier 3": "Iraq"}
    ])

# Spell checker to perfectly match your Google Sheet
TEAM_MAPPING = {
    "south korea": "Korea Republic", "korea": "Korea Republic", "korea republic": "Korea Republic",
    "turkey": "Türkiye", "türkiye": "Türkiye", "cote d'ivoire": "Côte D'Ivoire", "ivory coast": "Côte D'Ivoire",
    "curacao": "Curaçao", "curaçao": "Curaçao", "cape verde": "Cabo Verde", "cabo verde": "Cabo Verde",
    "usa": "USA", "united states": "USA", "bosnia": "Bosnia & Herzegovina", "bosnia and herzegovina": "Bosnia & Herzegovina",
    "bosnia & herzegovina": "Bosnia & Herzegovina", "congo dr": "Congo DR", "dr congo": "Congo DR"
}

def clean_name(name):
    return TEAM_MAPPING.get(str(name).strip().lower(), str(name).strip())

# ---------------------------------------------------------
# GOOGLE SHEET DATA STREAM
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def load_matches():
    try:
        # 🚨 PASTE YOUR GOOGLE SHEET LINK BETWEEN THE QUOTES ON THE LINE BELOW 🚨
        url = "https://docs.google.com/spreadsheets/d/1AcO04Psm2XkvEWB8KtSR8ux-20SmVeSF_AxnYp2Vkls/edit?usp=drivesdk"
        
        # Safety Check: If you forget to add the link, it warns you instead of crashing!
        if "PASTE" in url:
            st.warning("⚠️ **App paused:** Please go to line 87 in your GitHub code and paste your actual Google Sheet URL!")
            return pd.DataFrame()

        # Forces any URL format to convert safely to a background CSV export
        if "/edit" in url:
            csv_url = url.split("/edit")[0] + "/export?format=csv"
        else:
            csv_url = url
            
        df = pd.read_csv(csv_url)
        df.columns = [c.strip() for c in df.columns]
        
        if 'Team_1' not in df.columns or 'Team_2' not in df.columns:
            st.error("⚠️ **Column Error:** The app connected, but couldn't find exact 'Team_1' and 'Team_2' headers. Check your top row!")
            return pd.DataFrame()
            
        return df.dropna(subset=['Team_1', 'Team_2'])
    except Exception as e:
        st.error(f"Error loading matches from Google Sheets: {e}")
        return pd.DataFrame()

matches = load_matches()
draft_df = get_draft_data()

# Calculate Team Stats from your Match Log
team_records = {}
for _, row in matches.iterrows():
    t1 = clean_name(row['Team_1'])
    t2 = clean_name(row['Team_2'])
    
    try:
        s1, s2 = int(row['Team_1_Score']), int(row['Team_2_Score'])
    except:
        continue
        
    stage = str(row.get('Stage', 'Group')).strip()
        
    for t in [t1, t2]:
        if t not in team_records:
            team_records[t] = {"Win_Points": 0, "Draw_Points": 0, "Goals": 0, "Clean_Sheets": 0, "KO_Bonus": 0}
            
    team_records[t1]["Goals"] += s1
    team_records[t2]["Goals"] += s2
    
    if s2 == 0: team_records[t1]["Clean_Sheets"] += 1
    if s1 == 0: team_records[t2]["Clean_Sheets"] += 1
    
    if s1 > s2:
        if stage == "Group":
            team_records[t1]["Win_Points"] += 3
        else:
            if stage == "Round of 32": team_records[t1]["KO_Bonus"] += 5
            elif stage == "Round of 16": team_records[t1]["KO_Bonus"] += 10
            elif stage == "Quarter-Finals": team_records[t1]["KO_Bonus"] += 15
            elif stage == "Semi-Finals": team_records[t1]["KO_Bonus"] += 20
            elif stage == "3rd Place Match": team_records[t1]["KO_Bonus"] += 10
            elif stage == "Final": team_records[t1]["KO_Bonus"] += 25
            else:
                team_records[t1]["Win_Points"] += 3 
    elif s2 > s1:
        if stage == "Group":
            team_records[t2]["Win_Points"] += 3
        else:
            if stage == "Round of 32": team_records[t2]["KO_Bonus"] += 5
            elif stage == "Round of 16": team_records[t2]["KO_Bonus"] += 10
            elif stage == "Quarter-Finals": team_records[t2]["KO_Bonus"] += 15
            elif stage == "Semi-Finals": team_records[t2]["KO_Bonus"] += 20
            elif stage == "3rd Place Match": team_records[t2]["KO_Bonus"] += 10
            elif stage == "Final": team_records[t2]["KO_Bonus"] += 25
            else:
                team_records[t2]["Win_Points"] += 3 
    else:
        team_records[t1]["Draw_Points"] += 1
        team_records[t2]["Draw_Points"] += 1

# Build Leaderboard with Elimination Logic
leaderboard = []
for _, row in draft_df.iterrows():
    player = row["Player"]
    t1, t2, t3 = clean_name(row["Tier 1"]), clean_name(row["Tier 2"]), clean_name(row["Tier 3"])
    
    p_win, p_draw, p_goals, p_cs, p_ko, p_total = 0, 0, 0, 0, 0, 0
    active_count = 3
    
    for t in [t1, t2, t3]:
        # Check for elimination
        if t in ELIMINATED_TEAMS:
            active_count -= 1
            
        if t in team_records:
            stats = team_records[t]
            t_total = stats["Win_Points"] + stats["Draw_Points"] + stats["Goals"] + (stats["Clean_Sheets"] * 2) + stats["KO_Bonus"]
            
            p_win += stats["Win_Points"]
            p_draw += stats["Draw_Points"]
            p_goals += stats["Goals"]
            p_cs += stats["Clean_Sheets"]
            p_ko += stats["KO_Bonus"]
            p_total += t_total
            
    # Determine Status Display (Clean Emojis Only!)
    if active_count == 3:
        status = "🟢"
    elif active_count == 2:
        status = "🟡"
    elif active_count == 1:
        status = "🔴"
    else:
        status = "💀"
        
    math_breakdown = f"{p_win} (Win) + {p_draw} (Draw) + {p_goals} (Goals) + {p_cs * 2} (CS) + {p_ko} (KO) = {p_total}"
            
    leaderboard.append({
        "Rank": 0, 
        "Status": status,
        "Colleague": player, 
        "Tier 1": t1, 
        "Tier 2": t2, 
        "Tier 3": t3,
        "Math Breakdown": math_breakdown, 
        "Total Points": p_total
    })

leaderboard_df = pd.DataFrame(leaderboard)
if not leaderboard_df.empty:
    leaderboard_df = leaderboard_df.sort_values(by=["Total Points", "Math Breakdown"], ascending=False).reset_index(drop=True)
    leaderboard_df["Rank"] = leaderboard_df.index + 1

# ---------------------------------------------------------
# 2. LEADERBOARD (Full Width with Styling)
# ---------------------------------------------------------
st.subheader("🔥 Current Standings")

# Function to turn eliminated teams red
def color_eliminated_teams(val):
    if val in ELIMINATED_TEAMS:
        return 'color: #ff4b4b;' # Streamlit's native bright red
    return ''

if not leaderboard_df.empty:
    # Apply Pandas styling to center columns AND color the text
    try:
        styled_leaderboard = leaderboard_df.style.set_properties(
            subset=['Rank', 'Total Points', 'Status'], 
            **{'text-align': 'center'}
        ).map(
            color_eliminated_teams, 
            subset=['Tier 1', 'Tier 2', 'Tier 3']
        )
    except AttributeError:
        # Fallback for older versions of Pandas
        styled_leaderboard = leaderboard_df.style.set_properties(
            subset=['Rank', 'Total Points', 'Status'], 
            **{'text-align': 'center'}
        ).applymap(
            color_eliminated_teams, 
            subset=['Tier 1', 'Tier 2', 'Tier 3']
        )
    
    st.dataframe(
        styled_leaderboard, 
        hide_index=True,
        use_container_width=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Math Breakdown": st.column_config.TextColumn("Math Breakdown", help="Points from: Wins + Draws + Goals + Clean Sheets + Knockout Bonuses")
        }
    )
else:
    st.write("Waiting for match data to build the leaderboard...")

st.divider()

# ---------------------------------------------------------
# 3. MATCH LOG (Full Width)
# ---------------------------------------------------------
st.subheader("🏃 Played Matches Log")
if not matches.empty:
    st.dataframe(matches, hide_index=True, use_container_width=True)
else:
    st.write("No match history available yet.")
