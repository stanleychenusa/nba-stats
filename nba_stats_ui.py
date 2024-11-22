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

def get_player_stat_avg(player_name, stat_category, matchup, stat_amount): # need to add stat_amount as parameter
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
        st.warning(f"No games found for {player_name} against opponent '{matchup.upper()}'.")

    # [Algorithm's prediction] Calculate the statistic averages
    stat_avg_last10all = gamelog_df[stat_category].head(10).mean()
    stat_avg_last3opp = gamelog_df_opp[stat_category].head(3).mean()
    stat_avg_adjusted = stat_avg_last10all*0.75 + stat_avg_last3opp*0.25
    if gamelog_df_opp.empty:
        stat_avg_adjusted = stat_avg_last10all

    comparison = (
        f"Average {stat_category.upper()} for {player_name} over the past 10 games: {stat_avg_last10all:.1f}\n\n"
        f"Average {stat_category.upper()} for {player_name} over the past 3 games played against {matchup.upper()}: {stat_avg_last3opp:.1f}\n\n"
    )
    
    # Compare to stat_amount
    if stat_avg_adjusted > stat_amount:
        comparison += f"The algorithm's prediction of {stat_avg_adjusted:.3f} {stat_category.upper()} is **higher** than the specified {stat_amount:.1f} {stat_category.upper()}. Bet the **over**."
    elif stat_avg_adjusted < stat_amount:
        comparison += f"The algorithm's prediction of {stat_avg_adjusted:.3f} {stat_category.upper()} is **lower** than the specified {stat_amount:.1f} {stat_category.upper()}. Bet the **under**."
    else:
        comparison += f"The algorithm's prediction of {stat_avg_adjusted:.3f} {stat_category.upper()} is **equal** to the specified {stat_amount:.1f} {stat_category.upper()}. Use your best judgment."
    
    return comparison

# Streamlit App
st.title("Over/Under")
st.subheader("nba-stats")

# Input fields
player_name = st.text_input("Enter player's name:", value="")

stat_category = st.selectbox(
    "Select statistic category:",
    ["Select...", "PTS", "REB", "AST", "STL", "BLK", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT",
     "OREB", "DREB", "TOV", "PF", "MIN", "PLUS_MINUS"]
)
if stat_category == "Select...":
    stat_category = None

matchup = st.selectbox(
    "Select opponent:",
    ["Select...", "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW", "HOU", "IND",
     "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK", "OKC", "ORL", "PHI", "PHX",
     "POR", "SAC", "SAS", "TOR", "UTA", "WSH"]
)
if matchup == "Select...":
    matchup = None

stat_amount = st.number_input("Enter statistic amount to compare:", value=10.5, step=1.0, format="%.1f")
if stat_amount == 0:
    stat_amount = None

if st.button("Get Stats"):
    if player_name and stat_category and matchup:
        with st.spinner("Fetching data..."):
            result = get_player_stat_avg(player_name, stat_category, matchup, stat_amount)
        
        if "not found" in result or "No games" in result:
            st.error(result)
        else:
            st.markdown("### Results:")
            st.success(result)
    else:
        st.warning("Please fill in all fields.")
