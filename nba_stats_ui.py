import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll

@st.cache_data
def fetch_gamelog(player_id):
    try:
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=SeasonAll.all)
        return gamelog.get_data_frames()[0]
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def get_player_stat_avg(player_name, stat_category, matchup): # need to add stat_amount as parameter
    player_dict = players.get_players()

    # Find the player by name
    player = [player for player in player_dict if player['full_name'].lower() == player_name.lower()]
    if not player:
        return f"Player {player_name} not found."
    player_id = player[0]['id']

    # Fetch the player's game log for all seasons
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=SeasonAll.all)
    gamelog_df = gamelog.get_data_frames()[0]

    gamelog_df.columns = gamelog_df.columns.str.lower()
    stat_category = stat_category.lower()

    if stat_category not in gamelog_df.columns:
        return f"Statistic category '{stat_category}' not found."

    # Filter for the specified opponent
    matchup = matchup.lower()
    gamelog_df_opp = gamelog_df[gamelog_df['matchup'].str.contains(f" {matchup}", case=False, na=False)]
    if gamelog_df_opp.empty:
        return f"No games found for {player_name} against opponent '{matchup}'."

    # Calculate the averages
    stat_avg_last10all = gamelog_df[stat_category].head(10).mean()
    stat_avg_last3opp = gamelog_df_opp[stat_category].head(3).mean()

    return f"Average {stat_category} for {player_name} throughout the past 10 games: {stat_avg_last10all:.1f}\nAverage {stat_category} for {player_name} over the past 3 games played against {matchup.upper()}: {stat_avg_last3opp:.1f}"

# Streamlit App
st.title("NBA Player Stats Lookup")

# Input fields
player_name = st.text_input("Enter player's name:", value="")

stat_category = st.selectbox(
    "Select statistic category:",
    ["Select...", "PTS", "REB", "AST", "STL", "BLK", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT",
     "OREB", "DREB", "TOV", "PF", "MIN", "PLUS_MINUS"]
)
if stat_category == "Select...":
    stat_category = None

# stat_amount = st.number_input("Enter statistic amount:", min_value=0, value=10.5)
# if stat_amount == 0:
#     stat_amount = None

matchup = st.selectbox(
    "Select opponent:",
    ["Select...", "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW", "HOU", "IND",
     "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK", "OKC", "ORL", "PHI", "PHX",
     "POR", "SAC", "SAS", "TOR", "UTA", "WSH"]
)
if matchup == "Select...":
    matchup = None

if st.button("Get Stats"):
    if player_name and stat_category and matchup:
        result = get_player_stat_avg(player_name, stat_category, matchup) # need to add stat_amount as parameter
        st.write(result)
    else:
        st.write("Please fill in all fields.")
