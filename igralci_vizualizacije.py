###Priprava vizualizacij za zavihek Igralci

import random

import pandas as pd
import plotly.graph_objects as go
import psycopg2
import plotly.express as px

import Data.auth_public as auth

connection = auth.connect()
folder_path = "/Users/valgroleger/Svetovna-prvenstva-v-nogometu/views/graphs"


goals_players = """SELECT CASE
 WHEN p.given_name = 'not applicable' THEN p.family_name
 ELSE CONCAT(p.family_name || ' ', p.given_name) END
AS player_name, t.team_name AS team, count(DISTINCT g.goal_id) AS goals FROM players p
JOIN goals g ON p.player_id = g.player_id
JOIN player_appearances pa ON pa.player_id = p.player_id
JOIN teams t ON pa.team_id = t.team_id
GROUP BY player_name, t.team_name
ORDER BY goals desc
"""
df1 = pd.read_sql_query(goals_players, connection)

fig1 = go.Figure()

fig1.add_trace(
    go.Bar(
        x = df1["player_name"],
        y = df1["goals"]
    )
)

fig1.update_layout(
    margin=dict(l=0,r=0,b=0,t=0),
    paper_bgcolor = "#C5C6D0"
)

file_path1 = f"{folder_path}/goals_p.html"
fig1.write_html(file_path1, include_plotlyjs="cdn")
"""
for country in df1['team'].unique():
    # Filter the DataFrame for the current country
    filtered_df = df1[df1['team'] == country]
    
    # Add a trace for each country
    fig1.add_trace(
        go.Bar(
            x=filtered_df['player_name'],
            y=filtered_df['goals'],
            name=country,
            width = 0.5
        )
    )
    fig1.update_layout(
    title='Number of Goals by Player',
    xaxis_title='Player Names',
    yaxis_title='Number of Goals',
    #barmode='group',  # To group the bars by player
    legend_title='Country'  # Set the legend title
    )
"""

bookings_players = """SELECT CASE
 WHEN p.given_name = 'not applicable' THEN p.family_name
 ELSE CONCAT(p.family_name || ' ', p.given_name) END as player_name,
 COUNT(CASE when yellow_card = True THEN booking_id END) as num_yellow,
 COUNT(CASE when red_card = True THEN booking_id END) as num_red,
 COUNT(CASE when second_yellow_card = True THEN booking_id END) as num_second_yellow,
 COUNT(CASE when b.sending_off = True THEN booking_id END) as num_sending_off from bookings b
JOIN players p on b.player_id = p.player_id
group by player_name
ORDER BY num_yellow desc, num_red desc, num_second_yellow desc, num_sending_off desc
LIMIT 200;
"""

df2 = pd.read_sql_query(bookings_players, connection)

fig2 = go.Figure()

fig2.add_trace(
    go.Bar(
        x = df2['player_name'],
        y = df2['num_yellow'],
        name='Number of yellow cards',
        width = 0.7
    )
)

fig2.add_trace(
    go.Bar(
        x = df2['player_name'],
        y = df2['num_red'],
        name='Number of red cards',
        base = df2['num_yellow'],
        width = 0.7
    )
)

fig2.add_trace(
    go.Bar(
        x = df2['player_name'],
        y = df2['num_second_yellow'],
        name='Number of second yellow cards',
        base = df2['num_yellow'] + df2['num_red'],
        width = 0.7
    )
)

fig2.add_trace(
    go.Line(
        x = df2['player_name'],
        y = df2['num_sending_off'],
        name = "Number of sending-offs",
        line=dict(color="cyan"),
        fill = "tonexty"
    )
)

fig2.update_layout(
    title = 'Top 100 Players per Booking',
    xaxis_title="Player",
    yaxis_title="Number of Bookings",
    barmode='stack', 
    showlegend=True
)

fig2.update_layout(
    margin=dict(l=0,r=0,b=0,t=0),
    paper_bgcolor = "#C5C6D0"
)

file_path2 = f"{folder_path}/bookings_p.html"
fig2.write_html(file_path2, include_plotlyjs="cdn")

players_awards = """
SELECT  c.confederation_code, t.team_name,
case  WHEN p.given_name = 'not applicable' THEN p.family_name
 ELSE CONCAT(p.family_name || ' ', p.given_name) END as player_name,  count(Distinct award_id) AS num_of_awards FROM award_winners a
JOIN players p ON a.player_id = p.player_id
join player_appearances pa on p.player_id = pa.player_id
join teams t on pa.team_id = t.team_id
join confederations c on c.confederation_id = t.confederation_id
GROUP BY t.team_name, player_name, c.confederation_code
order by num_of_awards DESC;
"""

df3 = pd.read_sql_query(players_awards, connection)

fig3 = px.treemap(df3, path=["confederation_code","team_name", "player_name"], values=df3["num_of_awards"])

fig3.update_layout(
    margin=dict(l=0,r=0,b=0,t=0),
    paper_bgcolor = "#C5C6D0"
)

file_path3 = f"{folder_path}/awards_p.html"
fig3.write_html(file_path3, include_plotlyjs="cdn")

age_goals = """SELECT case
 WHEN p.given_name = 'not applicable' then p.family_name
 ELSE CONCAT(p.family_name || ' ', p.given_name) END
AS player_name,
COUNT(DISTINCT pa.match_id) AS appearances,
count(DISTINCT g.goal_id) AS goals,
AVG(CAST(RIGHT(pa.tournament_id, 4) AS INT)  - EXTRACT('YEAR' FROM p.birth_date)) as average_age,
CASE
 WHEN AVG(CAST(RIGHT(pa.tournament_id, 4) AS INT)  - EXTRACT('YEAR' FROM p.birth_date)) <= 24 then '<= 24 years' 
 when AVG(CAST(RIGHT(pa.tournament_id, 4) AS INT)  - EXTRACT('YEAR' FROM p.birth_date)) <= 31 then '< 24 <= 31 years'
 ELSE '> 31 years' END as age_group
FROM player_appearances pa
JOIN players p on p.player_id = pa.player_id
left JOIN goals g ON pa.player_id = g.player_id and pa.match_id = g.match_id
GROUP BY  player_name
ORDER BY age_group ASC, GOALS desc;
"""

df4 = pd.read_sql_query(age_goals, connection)

fig4 = px.scatter(df4, x = "average_age", y = "appearances",  trendline="ols",color = "goals", size="goals", hover_data="player_name")

fig4.update_layout(
    margin=dict(l=0,r=0,b=0,t=0),
    paper_bgcolor = "#C5C6D0"
)

file_path4 = f"{folder_path}/scatter_p.html"
fig4.write_html(file_path4, include_plotlyjs="cdn")