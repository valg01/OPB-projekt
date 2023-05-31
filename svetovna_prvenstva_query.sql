--numbers of goals scored by player
SELECT CASE
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
GROUP BY p.family_name, p.given_name, t.team_name
ORDER BY goals desc
LIMIT 100;

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
SELECT  t.team_name, c.confederation_code, award_name, count(award_id) AS num_of_awards FROM award_winners a
JOIN players p ON a.player_id = p.player_id
join player_appearances pa on p.player_id = pa.player_id
join teams t on pa.team_id = t.team_id
join confederations c on c.confederation_id = t.confederation_id
GROUP BY t.team_name, c.confederation_code, a.award_name 
order by num_of_awards DESC;

DROP VIEW players_age;
---starost igralcev na posameznih turnirjih (uporabi se view, da ga lahko še polj kličeva)
CREATE VIEW players_age AS(
SELECT CAST(RIGHT(pa.tournament_id, 4) AS INT)  - EXTRACT('YEAR' FROM p.birth_date) as age,
CASE
 WHEN p.given_name = 'not applicable' then p.family_name
 ELSE CONCAT(p.family_name || ' ', p.given_name) END
AS player_name,
te.team_name,
t.tournament_name,
t.host_country
FROM player_appearances pa
JOIN players p on p.player_id = pa.player_id
JOIN tournaments t on t.tournament_id = pa.tournament_id
JOIN teams te on pa.team_id = te.team_id
)


--Najmlajših 500 igralcev
CREATE TEMP TABLE temp2 AS
SELECT DISTINCT * FROM players_age
order by age ASC
LIMIT 500;

--Najstarejših 500 igralcev
CREATE TEMPORARY TABLE temp1 AS
SELECT DISTINCT * FROM players_age
order by age DESC
LIMIT 500;

--Države, ki imajo največ starih igralcev
select team_name, count(player_name) AS number
from temp1
GROUP BY team_name
ORDER by number DESC;

--Države, ki imajo največ mladih igralcev
select team_name, count(player_name) AS number
from temp2
GROUP BY team_name
ORDER by number DESC;

--number of substitutions per match
SELECT m.match_name, t.tournament_name, COALESCE(sum(CASE WHEN pa.substitute THEN 1 ELSE 0 END)) as substitutions  FROM matches m 
right join player_appearances pa on pa.match_id = m.match_id
JOIN tournaments t on t.tournament_id = m.tournament_id
GROUP BY m.match_name, t.tournament_name
order by tournament_name asc;

--number of red cards per turnament
select left(t.tournament_name, 4) AS tournament, count(b.booking_id) AS nm_bookings FROM bookings b
JOIN tournaments t ON t.tournament_id = b.tournament_id
GROUP BY tournament_name, b.red_card
HAVING b.red_card = 'True'
ORDER BY tournament_name;



