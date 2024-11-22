import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll

def get_player_stat_avg(player_name, stat_category, num_games, matchup):
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
    gamelog_df = gamelog_df[gamelog_df['matchup'].str.contains(f" {matchup}", case=False, na=False)]
    if gamelog_df.empty:
        return f"No games found for {player_name} against opponent '{matchup}'."

    # Filter the most recent num_games and calculate the average
    recent_games = gamelog_df.head(num_games)
    stat_avg = round(recent_games[stat_category].mean(), 2)

    return f"Average {stat_category} for {player_name} over the past {num_games} games played against {matchup.upper()}: {stat_avg:.2f}"

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

num_games = st.number_input("Enter the number of recent games:", min_value=0, max_value=82, value=3)
if num_games == 0:
    num_games = None

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
        result = get_player_stat_avg(player_name, stat_category, num_games, matchup)
        st.write(result)
    else:
        st.write("Please fill in all fields.")
