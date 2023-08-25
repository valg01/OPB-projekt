

##### Vizualiyacije Hall Of Fame
import random

import pandas as pd
import plotly.graph_objects as go
import psycopg2

import Data.auth_public as auth

folder_path = "/Users/valgroleger/Svetovna-prvenstva-v-nogometu/views/graphs"


headerColor = 'grey'
rowEvenColor = 'lightgrey'
rowOddColor = 'white'

connection = auth.connect()


####TABELA 1:
top_ten_wins = """SELECT
team_name as Country,
COALESCE(sum(CASE WHEN win THEN 1 ELSE 0 END),0) as Wins
FROM
(SELECT split_part(score, '–',1) as goals
--,home_team_id
,home_team_win as win
,team_name
,t.team_id
,'home' as played
FROM MATCHES m
LEFT JOIN teams t ON m.home_team_id = t.team_id
UNION ALL
--away teams
SELECT split_part(score, '–',2) as goals
--,away_team_id
,away_team_win as win
,team_name
,t.team_id
,'away' as played
FROM MATCHES m
LEFT JOIN teams t ON m.away_team_id = t.team_id) tab
GROUP BY team_name
ORDER BY Wins DESC
LIMIT 10;
"""

df1 = pd.read_sql_query(top_ten_wins, connection)

fig1 = go.Figure()
fig1.add_trace(
    go.Table(
        header = dict(values=["Country","Number Of Wins"],
            line_color='darkslategray',
            fill_color=headerColor,
            align=['center','center'],
            font=dict(color='white', size=18)),
        cells =  dict(values = [df1["country"], df1["wins"]],
                    line_color='darkslategray',
                    fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor,rowEvenColor,rowOddColor,rowEvenColor,rowOddColor,rowEvenColor]*2],
                    align = ['center', 'center'],
                    font = dict(color = 'darkslategray', size = 12)  )
    )
)

###fig.show()

file_path1 = f"{folder_path}/top_wins.html"
fig1.write_html(file_path1, include_plotlyjs="cdn")

####TABELA 2:

top_ten_goals= """SELECT CASE
 WHEN p.given_name = 'not applicable' THEN p.family_name
 ELSE CONCAT(p.family_name || ' ', p.given_name) END
AS player_name, t.team_name AS team, count(DISTINCT g.goal_id) AS goals FROM players p
JOIN goals g ON p.player_id = g.player_id
JOIN player_appearances pa ON pa.player_id = p.player_id
JOIN teams t ON pa.team_id = t.team_id
GROUP BY p.family_name, p.given_name, t.team_name
ORDER BY goals desc
LIMIT 10;
"""

df2 = pd.read_sql_query(top_ten_goals, connection)

fig2 = go.Figure()
fig2.add_trace(
    go.Table(
        header = dict(values=["Country","Player", "Goals"],
            line_color='darkslategray',
            fill_color=headerColor,
            align=['center','center', 'center'],
            font=dict(color='white', size=18)),
        cells =  dict(values = [df2["team"], df2["player_name"], df2["goals"]],
                    line_color='darkslategray',
                    fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor,rowEvenColor,rowOddColor,rowEvenColor,rowOddColor,rowEvenColor]*3],
                    align = ['center', 'center', 'center'],
                    font = dict(color = 'darkslategray', size = 12)  )
    )
)

file_path2 = f"{folder_path}/top_goals.html"
fig2.write_html(file_path2, include_plotlyjs="cdn")


####3. TABELA
top_ten_appearances = """select team_name as team, team_code as code, COUNT(DISTINCT tournament_id) AS num_on_a_tournament from qualified_teams
GROUP BY team_name, team_code
ORDER BY num_on_a_tournament DESC
LIMIT 10;"""

df3 = pd.read_sql_query(top_ten_appearances, connection)

fig3 = go.Figure()
fig3.add_trace(
    go.Table(
        header = dict(values=["Country","Code", "# Qualified"],
            line_color='darkslategray',
            fill_color=headerColor,
            align=['center','center', 'center'],
            font=dict(color='white', size=18)),
        cells =  dict(values = [df3["team"], df3["code"], df3["num_on_a_tournament"]],
                    line_color='darkslategray',
                    fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor,rowEvenColor,rowOddColor,rowEvenColor,rowOddColor,rowEvenColor]*3],
                    align = ['center', 'center', 'center'],
                    font = dict(color = 'darkslategray', size = 12)  )
    )
)

file_path3 = f"{folder_path}/top_app.html"
fig3.write_html(file_path3, include_plotlyjs="cdn")

top_ten_cs = """SELECT --mg.match_id,
 CASE
 WHEN p.given_name = 'not applicable' THEN p.family_name
 ELSE CONCAT(p.family_name || ' ', p.given_name) END
AS player_name, t.team_name AS team, --mg.match_id, p.goal_keeper, --score,
SUM(CASE WHEN goals_other = '0' THEN 1 
ELSE 0 END) AS clean_sheet
FROM players p
JOIN player_appearances pa ON pa.player_id = p.player_id
JOIN teams t ON pa.team_id = t.team_id
--JOIN matches m on m.match_id = pa.match_id
inner join match_goals mg on mg.match_id = pa.match_id and pa.team_id = mg.team_id
where p.goal_keeper = true
GROUP BY player_name, team --, mg.match_id
ORDER BY clean_sheet desc
limit 10;
"""

df4 = pd.read_sql_query(top_ten_cs, connection)

fig4 = go.Figure()
fig4.add_trace(
    go.Table(
        header = dict(values=["Country","Goal Keeper", "# Clean Sheets"],
            line_color='darkslategray',
            fill_color=headerColor,
            align=['center','center', 'center'],
            font=dict(color='white', size=18)),
        cells =  dict(values = [df4["team"], df4["player_name"], df4["clean_sheet"]],
                    line_color='darkslategray',
                    fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor,rowEvenColor,rowOddColor,rowEvenColor,rowOddColor,rowEvenColor]*3],
                    align = ['center', 'center', 'center'],
                    font = dict(color = 'darkslategray', size = 12)  )
    )
)

file_path4 = f"{folder_path}/top_cs.html"
fig4.write_html(file_path4, include_plotlyjs="cdn")