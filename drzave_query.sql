---ZAVIHEK DRŽAVE


--gostovanja po državah
SELECT c.confederation_code as ConfederationCode
--, c.confederation_name as ConfederationName
, tour.host_country
, COUNT(DISTINCT tournament_id) 
from tournaments tour
join teams t on t.team_name = tour.host_country
join confederations c on c.confederation_id = t.confederation_id
group by c.confederation_code, tour.host_country;

--Nagrade po državah
SELECT  t.team_name, c.confederation_code, award_name, count(award_id) AS num_of_awards FROM award_winners a
JOIN players p ON a.player_id = p.player_id
join player_appearances pa on p.player_id = pa.player_id
join teams t on pa.team_id = t.team_id
join confederations c on c.confederation_id = t.confederation_id
GROUP BY t.team_name, c.confederation_code, a.award_name 
order by num_of_awards DESC;

--povprečna starost igralcev po turnerjih in državah
select tournament_name, team_name, AVG(age) as average_age
from players_age
GROUP BY tournament_name, team_name
ORDER BY average_age ASC;

-- goli po drzavah 
SELECT  t.team_name AS team
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

--položaji po državah
SELECT t.team_name as team,
COUNT(CASE WHEN "position" = 1 then ts.team_id END) as winners,
COUNT(CASE WHEN "position" = 2 then ts.team_id END) as runnerups,
COUNT(CASE WHEN "position" = 3 then ts.team_id END) as third,
COUNT(CASE WHEN "position" = 4 then ts.team_id END) as fourth
FROM tournament_standings ts
join teams t on t.team_id = ts.team_id
GROUP BY t.team_name
order by winners desc, runnerups desc, third desc, fourth DESC, team asc;