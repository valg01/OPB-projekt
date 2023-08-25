###Države zavihek priprava vizualizacij
import random

import pandas as pd
import plotly.graph_objects as go
import psycopg2
import plotly.express as px

import Data.auth_public as auth

connection = auth.connect()
folder_path = "/Users/valgroleger/Svetovna-prvenstva-v-nogometu/views/graphs"


tournament_country = """SELECT --c.confederation_code as ConfederationCode
c.confederation_name as ConfederationName
, tour.host_country
, COUNT(DISTINCT tournament_id) as num
from tournaments tour
join teams t on t.team_name = tour.host_country
join confederations c on c.confederation_id = t.confederation_id
group by ConfederationName, tour.host_country;
"""

df1 = pd.read_sql_query(tournament_country, connection)

fig1 = px.treemap(df1, path=["confederationname", "host_country"], values=df1["num"])

fig1.update_layout(
    title="Number of tournaments per confederation and country",
    margin=dict(t=40, l=0, r=0, b=0),
)

file_path1 = f"{folder_path}/tour_country.html"
fig1.write_html(file_path1, include_plotlyjs="cdn")

awards_country = """SELECT  t.team_name,
-- c.confederation_code,
 award_name, count(award_id) AS num_of_awards FROM award_winners a
JOIN players p ON a.player_id = p.player_id
join player_appearances pa on p.player_id = pa.player_id
join teams t on pa.team_id = t.team_id
join confederations c on c.confederation_id = t.confederation_id
GROUP BY t.team_name, c.confederation_code, a.award_name 
order by num_of_awards desc, award_name DESC;
"""

df2 = pd.read_sql_query(awards_country, connection)
fig2 = go.Figure()
for award_name in df2['award_name'].unique():
    award_data = df2[df2['award_name'] == award_name]
    team_names = award_data['team_name']
    num_of_awards = award_data['num_of_awards']



    fig2.add_trace(
        go.Bar(
            y = num_of_awards,
            x = team_names,
            name = award_name
        )
    )

fig2.update_layout(
    title="Number of Awards by Team",
    xaxis_title="Teams",
    yaxis_title="Number of awards",
    barmode='stack',
)

file_path2 = f"{folder_path}/awards_c.html"
fig2.write_html(file_path2, include_plotlyjs="cdn")

age_country_tournament = """select tournament_name, team_name, AVG(age) as average_age
from players_age
GROUP BY tournament_name, team_name
ORDER BY tournament_name ASC, average_age ASC;
"""
df3 = pd.read_sql_query(age_country_tournament, connection)

fig3 = go.Figure()

for team in df3["team_name"].unique():
    team_data = df3[df3['team_name'] == team]
    fig3.add_trace(
        go.Line(
            x = team_data["tournament_name"],
            y = team_data["average_age"],
            mode = "lines+markers",
            name = team
        )
    )

fig3.update_layout(
    title="Average Age by Tournament and Team",
    xaxis_title="Tournament",
    yaxis_title="Average Age",
    xaxis=dict(type='category'),  # Use categorical x-axis
    showlegend=True
)
file_path3 = f"{folder_path}/age_t.html"
fig3.write_html(file_path3, include_plotlyjs="cdn")

goals_countries = """SELECT  t.team_name AS team
/*, COALESCE(sum(CASE WHEN p.goal_keeper THEN 1 ELSE 0 END)) as goals_keeper
, COALESCE(sum(CASE WHEN p.defender THEN 1 ELSE 0 END)) as goals_defender
, COALESCE(sum(CASE WHEN p.midfielder THEN 1 ELSE 0 END)) as goals_midfielder
, COALESCE(sum(CASE WHEN p.forward THEN 1 ELSE 0 END)) as goals_forward */
, COUNT(DISTINCT g.goal_id) as NumberOfGoals FROM players p
JOIN goals g ON p.player_id = g.player_id
JOIN player_appearances pa ON pa.player_id = p.player_id
JOIN teams t ON pa.team_id = t.team_id
GROUP BY  t.team_name
ORDER BY NumberOfGoals desc;
"""

df4 = pd.read_sql_query(goals_countries, connection)

fig4 = go.Figure()

fig4.add_trace(
    go.Pie(
        labels = df4["team"],
        values = df4["numberofgoals"],
        textinfo= "none"
    )
)

fig4.update_layout(
    showlegend = False
)

file_path4 = f"{folder_path}/goals_c.html"
fig4.write_html(file_path4, include_plotlyjs="cdn")

countires_position = """SELECT t.team_name as team,
COUNT(CASE WHEN "position" = 1 then ts.team_id END) as winners,
COUNT(CASE WHEN "position" = 2 then ts.team_id END) as runnerups,
COUNT(CASE WHEN "position" = 3 then ts.team_id END) as third,
COUNT(CASE WHEN "position" = 4 then ts.team_id END) as fourth
FROM tournament_standings ts
join teams t on t.team_id = ts.team_id
GROUP BY t.team_name
order by winners desc, runnerups desc, third desc, fourth DESC, team asc;
"""

df5 = pd.read_sql_query(countires_position, connection)

fig5 = go.Figure()

fig5.add_trace(
    go.Bar(
        x = df5["team"],
        y = df5["winners"],
        name = "Winners",
        marker_color = '#FFD700'
    )
)

fig5.add_trace(
    go.Bar(
        x = df5["team"],
        y = df5["runnerups"],
        name="Runner ups",
        base = df5["winners"],
        marker_color = "#C0C0C0"
    )
)

fig5.add_trace(
    go.Bar(
        x = df5["team"],
        y = df5["third"],
        name = "Third",
        base = df5["winners"] + df5["runnerups"],
        marker_color = "#CD7F32"
    )
)

fig5.add_trace(
    go.Bar(
        x = df5["team"],
        y = df5["fourth"],
        name = "Fourth",
        base = df5["winners"] + df5["runnerups"] + df5["third"],
        marker_color = "#A52A2A"
    )
)

fig5.update_layout(
    title="Tournament Performance by Team",
    xaxis_title="Team",
    yaxis_title="Number of Occurrences",
    barmode='stack',
    showlegend=True
)

file_path5 = f"{folder_path}/position.html"
fig5.write_html(file_path5, include_plotlyjs="cdn")