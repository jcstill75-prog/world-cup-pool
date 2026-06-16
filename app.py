import streamlit as st
import pandas as pd
import datetime

# Set premium dark and gold page layout
st.set_page_config(
    page_title="World Cup 2026 Office Sweepstakes",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; }
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    h1 { color: #D4AF37; } /* Gold Title */
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 World Cup 2026 Office Sweepstakes")
st.markdown("Track your live office standings! Synced with your official Google Sheet tournament records.")

# Maps standard alternative spellings to ensure perfect calculations with zero manual changes
TEAM_MAPPING = {
    "south korea": "Korea Republic",
    "korea": "Korea Republic",
    "republic of korea": "Korea Republic",
    "korea republic": "Korea Republic",
    "turkey": "Türkiye",
    "türkiye": "Türkiye",
    "cote d'ivoire": "Côte D'Ivoire",
    "cote d’ivoire": "Côte D'Ivoire",
    "ivory coast": "Côte D'Ivoire",
    "côte d'ivoire": "Côte D'Ivoire",
    "curacao": "Curaçao",
    "curaçao": "Curaçao",
    "cape verde": "Cabo Verde",
    "cabo verde": "Cabo Verde",
    "usa": "USA",
    "united states": "USA",
    "united states of america": "USA",
    "bosnia": "Bosnia & Herzegovina",
    "bosnia and herzegovina": "Bosnia & Herzegovina",
    "bosnia & herzegovina": "Bosnia & Herzegovina",
    "congo dr": "Congo DR",
    "dr congo": "Congo DR",
    "democratic republic of the congo": "Congo DR"
}

TEAM_EMOJIS = {
    "Germany": "🇩🇪", "Canada": "🇨🇦", "Panama": "🇵🇦",
    "Belgium": "🇧🇪", "Norway": "🇳🇴", "Qatar": "🇶🇦",
    "France": "🇫🇷", "Australia": "🇦🇺", "Jordan": "🇯🇴",
    "Colombia": "🇨🇴", "Egypt": "🇪🇬", "Algeria": "🇩🇿",
    "Mexico": "🇲🇽", "Korea Republic": "🇰🇷", "South Africa": "🇿🇦",
    "USA": "🇺🇸", "Japan": "🇯🇵", "Uzbekistan": "🇺🇿",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Senegal": "🇸🇳", "Bosnia & Herzegovina": "🇧🇦",
    "Brazil": "🇧🇷", "Czechia": "🇨🇿", "Cabo Verde": "🇨🇻",
    "Switzerland": "🇨🇭", "Türkiye": "🇹🇷", "Haiti": "🇭🇹",
    "Croatia": "🇭🇷", "Austria": "🇦🇹", "Saudi Arabia": "🇸🇦",
    "Portugal": "🇵🇹", "Ghana": "🇬🇭", "Curaçao": "🇨🇼",
    "Netherlands": "🇳🇱", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Congo DR": "🇨🇩",
    "Uruguay": "🇺🇾", "Paraguay": "🇵🇾", "Iran": "🇮🇷",
    "Morocco": "🇲🇦", "Sweden": "🇸🇪", "New Zealand": "🇳🇿",
    "Spain": "🇪🇸", "Tunisia": "🇹🇳", "Côte D'Ivoire": "🇨🇮",
    "Argentina": "🇦🇷", "Ecuador": "🇪🇨", "Iraq": "🇮🇶"
}

def clean_team_name(name):
    if not isinstance(name, str):
        return ""
    name_clean = name.strip().lower()
    return TEAM_MAPPING.get(name_clean, name.strip())

def get_emoji(team_name):
    return TEAM_EMOJIS.get(team_name, "🏳️")

# 100% accurate representation of your spreadsheet image. No colleagues.csv needed!
@st.cache_data
def get_draft_data():
    raw_data = [
        {"Player": "Amanda", "Tier_1": "Germany", "Tier_2": "Canada", "Tier_3": "Panama"},
        {"Player": "Ana", "Tier_1": "Belgium", "Tier_2": "Norway", "Tier_3": "Qatar"},
        {"Player": "Brian", "Tier_1": "France", "Tier_2": "Australia", "Tier_3": "Jordan"},
        {"Player": "Cassie", "Tier_1": "Colombia", "Tier_2": "Egypt", "Tier_3": "Algeria"},
        {"Player": "Craig", "Tier_1": "Mexico", "Tier_2": "Korea Republic", "Tier_3": "South Africa"},
        {"Player": "Emma", "Tier_1": "USA", "Tier_2": "Japan", "Tier_3": "Uzbekistan"},
        {"Player": "Jasmine (& Rob)", "Tier_1": "England", "Tier_2": "Senegal", "Tier_3": "Bosnia & Herzegovina"},
        {"Player": "Jennifer", "Tier_1": "Brazil", "Tier_2": "Czechia", "Tier_3": "Cabo Verde"},
        {"Player": "Le'Otis", "Tier_1": "Switzerland", "Tier_2": "Türkiye", "Tier_3": "Haiti"},
        {"Player": "Linda", "Tier_1": "Croatia", "Tier_2": "Austria", "Tier_3": "Saudi Arabia"},
        {"Player": "Mark", "Tier_1": "Portugal", "Tier_2": "Ghana", "Tier_3": "Curaçao"},
        {"Player": "Rebecca", "Tier_1": "Netherlands", "Tier_2": "Scotland", "Tier_3": "Congo DR"},
        {"Player": "Ramon", "Tier_1": "Uruguay", "Tier_2": "Paraguay", "Tier_3": "Iran"},
        {"Player": "Stacie", "Tier_1": "Morocco", "Tier_2": "Sweden", "Tier_3": "New Zealand"},
        {"Player": "Taliah", "Tier_1": "Spain", "Tier_2": "Tunisia", "Tier_3": "Côte D'Ivoire"},
        {"Player": "Tressa", "Tier_1": "Argentina", "Tier_2": "Ecuador", "Tier_3": "Iraq"}
    ]
    return pd.DataFrame(raw_data)

st.sidebar.header("⚙️ Dashboard Settings")

# Google Sheet Sharing Link Configuration (Preloaded with your actual sheet ID!)
default_url = "https://docs.google.com/spreadsheets/d/1AcO04Psm2XkvEWB8KtSR8ux-20SmVeSF_AxnYp2Vkls/edit?usp=sharing"
sheet_url = st.sidebar.text_input(
    "Google Sheet URL",
    value=default_url,
    help="Verify that your sheet link is public ('Anyone with the link can view')"
)

st.sidebar.markdown("---")
st.sidebar.subheader("💡 Point Scoring Customization")
match_win_pts = st.sidebar.number_input("Match Win Points", value=3, min_value=0)
match_draw_pts = st.sidebar.number_input("Match Draw Points", value=1, min_value=0)
goal_pts = st.sidebar.number_input("Points Per Goal", value=1, min_value=0)

# Optional clean sheet bonus toggle (Defaults to unchecked to match your current sheet calculations)
include_clean_sheet = st.sidebar.checkbox("Include Clean Sheet Bonus", value=False)
clean_sheet_pts = st.sidebar.number_input("Clean Sheet Bonus Points", value=2, min_value=0) if include_clean_sheet else 0

# Manual Cache Clear Button
if st.sidebar.button("🔄 Force Clear Cache & Refresh"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(f"Last synchronized: {datetime.datetime.now().strftime('%H:%M:%S')}")

@st.cache_data(ttl="5m")  # Refresh stream every 5 minutes
def load_matches(url):
    try:
        csv_url = url.split("/edit")[0] + "/gviz/tq?tqx=out:csv"
        matches_df = pd.read_csv(csv_url)
        
        # Verify columns are aligned
        expected = ['Stage', 'Team_1', 'Team_1_Score', 'Team_2', 'Team_2_Score']
        matches_df.columns = [c.strip() for c in matches_df.columns]
        
        matches_df = matches_df[expected].dropna(subset=['Team_1', 'Team_2'])
        return matches_df
    except Exception as e:
        st.error(f"❌ **Failed to load live Google Sheet:** {e}. Confirm your spreadsheet link remains public.")
        st.stop()

matches = load_matches(sheet_url)
draft_df = get_draft_data()

team_records = {}

for _, row in matches.iterrows():
    # Run the raw team names through the spell-checker
    t1 = clean_team_name(row['Team_1'])
    t2 = clean_team_name(row['Team_2'])
    
    # Skip unfinished/empty games safely
    try:
        s1 = int(row['Team_1_Score'])
        s2 = int(row['Team_2_Score'])
    except (ValueError, TypeError):
        continue  
        
    # Initialize dictionary records if team is not yet registered
    for team in [t1, t2]:
        if team not in team_records:
            team_records[team] = {
                "Wins": 0, "Draws": 0, "Losses": 0, 
                "Goals_Scored": 0, "Clean_Sheets": 0, "Match_Points": 0
            }
            
    # Track Goals Scored
    team_records[t1]["Goals_Scored"] += s1
    team_records[t2]["Goals_Scored"] += s2
    
    # Calculate Clean Sheets
    if s2 == 0:
        team_records[t1]["Clean_Sheets"] += 1
    if s1 == 0:
        team_records[t2]["Clean_Sheets"] += 1
        
    # Match Winners & Draw Allocations
    if s1 > s2:
        team_records[t1]["Wins"] += 1
        team_records[t1]["Match_Points"] += match_win_pts
        team_records[t2]["Losses"] += 1
    elif s2 > s1:
        team_records[t2]["Wins"] += 1
        team_records[t2]["Match_Points"] += match_win_pts
        team_records[t1]["Losses"] += 1
    else:
        team_records[t1]["Draws"] += 1
        team_records[t1]["Match_Points"] += match_draw_pts
        team_records[t2]["Draws"] += 1
        team_records[t2]["Match_Points"] += match_draw_pts

# Convert nested dictionary to formatted DataFrame
team_data_list = []
for team, stats in team_records.items():
    # Points Formula: Match Wins/Draws Points + Goals Scored + Clean Sheets (if enabled)
    total_pts = stats["Match_Points"] + (stats["Goals_Scored"] * goal_pts) + (stats["Clean_Sheets"] * clean_sheet_pts)
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

if teams_df.empty:
    teams_df = pd.DataFrame(columns=["Team", "Wins", "Draws", "Losses", "Goals Scored", "Clean Sheets", "Total Points"])

leaderboard_list = []

for _, row in draft_df.iterrows():
    player = row["Player"]
    t1 = clean_team_name(row["Tier_1"])
    t2 = clean_team_name(row["Tier_2"])
    t3 = clean_team_name(row["Tier_3"])
    
    p_pts = 0
    p_goals = 0
    p_clean_sheets = 0
    p_total = 0
    
    detailed_teams = []
    
    # Calculate performance for each tier
    for tier_num, team in enumerate([t1, t2, t3], start=1):
        team_display_name = f"{get_emoji(team)} {team}"
        
        if team in teams_df["Team"].values:
            t_row = teams_df[teams_df["Team"] == team].iloc[0]
            t_pts = team_records[team]["Match_Points"]
            t_goals = t_row["Goals Scored"]
            t_clean_sheets = t_row["Clean Sheets"]
            
            # Aggregate metrics for the player
            p_pts += t_pts
            p_goals += t_goals
            p_clean_sheets += t_clean_sheets
            
            # Country-specific points calculation
            c_total = t_pts + (t_goals * goal_pts) + (t_clean_sheets * clean_sheet_pts)
            p_total += c_total
            
            detailed_teams.append(f"{team_display_name} ({c_total} pts)")
        else:
            detailed_teams.append(f"{team_display_name} (0 pts)")
            
    leaderboard_list.append({
        "Leaderboard Rank": 1,
        "Player": player,
        "Tier 1: Favourite": detailed_teams[0],
        "Tier 2: Mid-Tier": detailed_teams[1],
        "Tier 3: Underdog": detailed_teams[2],
        "Points": p_pts,
        "Goals": p_goals,
        "Clean Sheets": p_clean_sheets,
        "Total": p_total
    })

leaderboard_df = pd.DataFrame(leaderboard_list)

# Sort leaderboard descending based on Total, then Goals, then Points
if not leaderboard_df.empty:
    leaderboard_df = leaderboard_df.sort_values(
        by=["Total", "Goals", "Points"], 
        ascending=False
    ).reset_index(drop=True)
    leaderboard_df["Leaderboard Rank"] = leaderboard_df.index + 1
else:
    leaderboard_df = pd.DataFrame(columns=["Leaderboard Rank", "Player", "Tier 1: Favourite", "Tier 2: Mid-Tier", "Tier 3: Underdog", "Points", "Goals", "Total"])

# Drop columns dynamically if clean sheets are turned off in settings to clean UI space
final_columns = ["Leaderboard Rank", "Player", "Tier 1: Favourite", "Tier 2: Mid-Tier", "Tier 3: Underdog", "Points", "Goals", "Total"]
if include_clean_sheet:
    final_columns.insert(7, "Clean Sheets")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Matches Played", len(matches))
with col2:
    if not leaderboard_df.empty:
        top_player = leaderboard_df.iloc[0]["Player"]
        top_score = leaderboard_df.iloc[0]["Total"]
        st.metric("Sweepstakes Leader", f"{top_player}", f"{top_score} points")
    else:
        st.metric("Sweepstakes Leader", "N/A", "0 points")
with col3:
    if not teams_df.empty:
        high_scorer = teams_df.sort_values(by="Goals Scored", ascending=False).iloc[0]["Team"]
        high_score = teams_df.sort_values(by="Goals Scored", ascending=False).iloc[0]["Goals Scored"]
        st.metric("Top Scoring Team", f"{get_emoji(high_scorer)} {high_scorer}", f"{high_score} goals")
    else:
        st.metric("Top Scoring Team", "N/A")
with col4:
    total_goals = teams_df["Goals Scored"].sum() // 2 if not teams_df.empty else 0
    st.metric("Tournament Goals", f"{total_goals}")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🏆 Leaderboard Standings", "⚽ Live Match Logs", "📊 Team Performance Metrics"])

with tab1:
    st.subheader("Leaderboard Standings")
    st.dataframe(
        leaderboard_df[final_columns].set_index("Leaderboard Rank"), 
        use_container_width=True
    )
    
    # Standings Bar Chart
    if not leaderboard_df.empty:
        st.subheader("Live Standing Gaps")
        chart_data = leaderboard_df.set_index("Player")[["Total"]]
        st.bar_chart(chart_data, color="#D4AF37")

with tab2:
    st.subheader("Match Log History (Google Sheets Feed)")
    if matches.empty:
        st.write("Waiting for tournament match data streams.")
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
