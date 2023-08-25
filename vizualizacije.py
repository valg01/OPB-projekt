import random

import pandas as pd
import plotly.graph_objects as go
import psycopg2

import Data.auth_public as auth

connection = auth.connect()

nm_goals_player = """SELECT CASE
 WHEN p.given_name = 'not applicable' THEN p.family_name
 ELSE CONCAT(p.family_name || ' ', p.given_name) END
AS player_name, t.team_name AS team, count(DISTINCT g.goal_id) AS goals FROM players p
JOIN goals g ON p.player_id = g.player_id
JOIN player_appearances pa ON pa.player_id = p.player_id
JOIN teams t ON pa.team_id = t.team_id
--where 
--count_tournaments = 4 AND
--AND p.family_name = 'Rivaldo' AND
--p.goal_keeper = true and
--where p.given_name = 'Lothar'
GROUP BY p.family_name, p.given_name, t.team_name
ORDER BY goals desc
LIMIT 100;"""


"""""
fig = go.Figure()
for country in df['team'].unique():
    # Filter the DataFrame for the current country
    filtered_df = df[df['team'] == country]
    
    # Add a trace for each country
    fig.add_trace(
        go.Bar(
            x=filtered_df['player_name'],
            y=filtered_df['goals'],
            name=country,
            width = 0.5
        )
    )
    fig.update_layout(
    title='Number of Goals by Player',
    xaxis_title='Player Names',
    yaxis_title='Number of Goals',
    #barmode='group',  # To group the bars by player
    legend_title='Country'  # Set the legend title
    )
# fig = go.Figure(data=go.Bar(x=df['player_name'], y = df['goals']))
# fig.update_layout(
#     title='Number of Goals by Player',
#     xaxis_title='Player Names',
#     yaxis_title='Number of Goals'
# )

fig.show()
""" ""
"""""
df_sorted = df.sort_values('goals', ascending=False)

fig = go.Figure()
barve = {}
for drzava in df['team'].unique():
    one = random.randint(0,255)
    two = random.randint(0,255)
    three = random.randint(0,255)
    barve[drzava] = f"rgb({one}, {two}, {three})"

fig.add_trace(
    go.Bar(
        x=df_sorted['player_name'],
        y=df_sorted['goals'],
        marker_color=[barve.get(drzava, 'rgb(128, 128, 128)') for drzava in df_sorted['team']],  # Color bars by country
        name='Goals',
        width = 0.5
    )
)

fig.update_layout(
    title='Number of Goals by Player',
    xaxis_title='Player Names',
    yaxis_title='Number of Goals',
    legend_title='Country',  # Set the legend title
    barmode='group'  # Group the bars
)

fig.show()
"""
"""fig = go.Figure()

# Sort the DataFrame by 'goals' column in descending order
df_sorted = df.sort_values("goals", ascending=False)

for country in df_sorted["team"].unique():
    # Filter the DataFrame for the current country
    filtered_df = df_sorted[df_sorted["team"] == country]

    # Add a trace for each country
    fig.add_trace(
        go.Bar(
            x=filtered_df["player_name"],
            y=filtered_df["goals"],
            name=country,
            width=0.5,
        )
    )

fig.update_layout(
    title="Number of Goals by Player",
    xaxis_title="Player Names",
    yaxis_title="Number of Goals",
    # barmode='group',  # To group the bars by player
    legend_title="Country",  # Set the legend title
)

folder_path = "/Users/valgroleger/Svetovna-prvenstva-v-nogometu/views/graphs"
file_path1 = f"{folder_path}/goals.html"
fig.write_html(file_path1, include_plotlyjs="cdn")
# fig.show()

"""
conf_count_host = """SELECT c.confederation_code AS ConfederationCode
, c.confederation_name AS ConfederationName
, COUNT(DISTINCT tournament_id) AS number
FROM tournaments tour
JOIN teams t ON t.team_name = tour.host_country
JOIN confederations c ON c.confederation_id = t.confederation_id
GROUP BY c.confederation_code, c.confederation_name;"""

df2 = pd.read_sql_query(conf_count_host, connection)

fig2 = go.Figure(data=[go.Pie(labels=df2["confederationcode"], values=df2["number"])])

fig2.update_layout(
    title="Count of hosts by confederation",
)
# fig2.show()
"""file_path2 = f"{folder_path}/hosts.html"
fig2.write_html(file_path2, include_plotlyjs="cdn")"""

awards = """SELECT  t.team_name as team
, c.confederation_code as confederation_code
--, award_name
, count(award_id) AS num_of_awards
 FROM award_winners a
JOIN players p ON a.player_id = p.player_id
join player_appearances pa on p.player_id = pa.player_id
join teams t on pa.team_id = t.team_id
join confederations c on c.confederation_id = t.confederation_id
GROUP BY t.team_name, c.confederation_code --, a.award_name 
order by num_of_awards DESC;"""

df3 = pd.read_sql_query(awards, connection)

parent = []
for drzava in df3["team"].unique():
    parent.append("")

fig3 = go.Figure(
    go.Treemap(labels=df3["team"], parents=parent, values=df3["num_of_awards"])
)
fig3.update_layout(
    title="Number of individual awards by team",
)

# fig3.show()
"""file_path3 = f"{folder_path}/awards.html"
fig3.write_html(file_path3, include_plotlyjs="cdn")"""


red_cards = """SELECT LEFT(t.tournament_name, 4) AS tournament, count(b.booking_id) AS nm_bookings FROM bookings b
JOIN tournaments t ON t.tournament_id = b.tournament_id
GROUP BY tournament_name, b.red_card
HAVING b.red_card = 'True'
ORDER BY tournament_name;"""

df4 = pd.read_sql_query(red_cards, connection)

fig4 = go.Figure()

fig4.add_trace(
    go.Scatter(
        x=df4["tournament"],
        y=df4["nm_bookings"],
        mode="lines",
        name="Line",
        line=dict(color="red"),
    )
)

fig4.update_layout(
    title="Number of red cards per tournament",
    xaxis_title="Year",
    yaxis_title="Number of red cards",
)

# fig4.show()
"""file_path4 = f"{folder_path}/red_cards.html"
fig4.write_html(file_path4, include_plotlyjs="cdn")
"""
fig3.show()