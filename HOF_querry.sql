--HOF Tabele query

--1. TABELA: TOP 10 držav po zmagah

SELECT
team_name as Country,
COALESCE(sum(CASE WHEN win THEN 1 ELSE 0 END),0) as Wins
--Sum(goals) as Goals_scored FROM
--home teams
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

--2.Tabela: Top 10 igralcev z največ goli
SELECT CASE
 WHEN p.given_name = 'not applicable' THEN p.family_name
 ELSE CONCAT(p.family_name || ' ', p.given_name) END
AS player_name, t.team_name AS team, count(DISTINCT g.goal_id) AS goals FROM players p
JOIN goals g ON p.player_id = g.player_id
JOIN player_appearances pa ON pa.player_id = p.player_id
JOIN teams t ON pa.team_id = t.team_id
GROUP BY p.family_name, p.given_name, t.team_name
ORDER BY goals desc
LIMIT 10;

--3. Tabela: Top 10 držav po nastopih
select team_name, team_code, COUNT(DISTINCT tournament_id) AS num_on_a_tournament from qualified_teams
GROUP BY team_name, team_code
ORDER BY num_on_a_tournament DESC
LIMIT 10;

--4. Tabela: top 10 golmanov po clean sheetih --- to bo treba še popravit oz posodobiti podatke

CREATE VIEW match_goals AS
SELECT split_part(score, '–',2) as goals_other
--,home_team_id
,home_team_win as win
,team_name
,t.team_id
,'home' as played
,match_id
FROM MATCHES m
LEFT JOIN teams t ON m.home_team_id = t.team_id
UNION ALL
--away teams
SELECT split_part(score, '–',1) as goals_other
--,away_team_id
,away_team_win as win
,team_name
,t.team_id
,'away' as played
,match_id
FROM MATCHES m
LEFT JOIN teams t ON m.away_team_id = t.team_id;

SELECT --mg.match_id,
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
