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
# To add more teams later, just add a comma and type their name in quotes!
ELIMINATED_TEAMS = [
    "Algeria", "Australia", "Austria", "Bosnia & Herzegovina", "Brazil", 
    "Cabo Verde", "Canada", "Congo DR", "Côte D'Ivoire", "Croatia", 
    "Curaçao", "Czechia", "Ecuador", "Egypt", "Germany", "Ghana", 
    "Haiti", "Iran", "Iraq", "Japan", "Jordan", "Korea Republic", 
    "Mexico", "Netherlands", "New Zealand", "Panama", "Paraguay", 
    "Portugal", "Qatar", "Saudi Arabia", "Scotland", "Senegal", 
    "South Africa", "Sweden", "Tunisia", "Türkiye", "Uruguay", 
    "USA", "Uzbekistan"
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
        # PASTE YOUR GOOGLE SHEET LINK BETWEEN THE QUOTES BELOW:
        url = "https://docs.google.com/spreadsheets/d/1AcO04Psm2XkvEWB8KtSR8ux-20SmVeSF_AxnYp2Vkls/edit?gid=2039619876#gid=2039619876"
        
        # Forces any URL format to convert safely to a background CSV export
        csv_url = url.split("/edit")[0] + "/export?format=csv"
        
        df = pd.read_csv(csv_url)
        df.columns = [c.strip() for
