--numbers of goals scored by player
select p.family_name as surname, p.given_name as name, t.team_name as team, count(DISTINCT g.goal_id) as goals from players p
join goals g on p.player_id = g.player_id
join player_appearances pa on pa.player_id = p.player_id
join teams t on pa.team_id = t.team_id
--where 
--count_tournaments = 4 AND
--AND p.family_name = 'Rivaldo' AND
--p.goal_keeper = true and
GROUP BY p.family_name, p.given_name, t.team_name
ORDER BY goals desc;

--Finds number of matches played at each stadium
SELECT s.stadium_name as stadium, s.city_name as city, s.country_name as country, COUNT(DISTINCT g.goal_id) as numOfGoals
from stadiums s
join matches m on m.stadium_id = s.stadium_id
JOIN goals g on g.match_id = m.match_id
GROUP BY s.stadium_name, s.city_name, s.country_name
ORDER BY numOfGoals asc ;


--confederation count of hosts

SELECT c.confederation_code as ConfederationCode
, c.confederation_name as ConfederationName
, COUNT(DISTINCT tournament_id) 
from tournaments tour
join teams t on t.team_name = tour.host_country
join confederations c on c.confederation_id = t.confederation_id
group by c.confederation_code, c.confederation_name;

--Years when hosts won
SELECT REPLACE(tournament_name, ' FIFA World Cup', '') as year, winner FROM tournaments
where winner = host_country;

--Goals scored by tournament and position
SELECT t.tournament_name as Tournament
, COALESCE(sum(CASE WHEN p.goal_keeper THEN 1 ELSE 0 END)) as goals_keeper
, COALESCE(sum(CASE WHEN p.defender THEN 1 ELSE 0 END)) as goals_defender
, COALESCE(sum(CASE WHEN p.midfielder THEN 1 ELSE 0 END)) as goals_midfielder
, COALESCE(sum(CASE WHEN p.forward THEN 1 ELSE 0 END)) as goals_forward
, COUNT(DISTINCT g.goal_id) as NumberOfGoals
FROM tournaments t
join goals g ON g.tournament_id = t.tournament_id
join players p on p.player_id = g.player_id
GROUP BY tournament_name
order by NumberOfGoals desc;

--Awards by countries 




