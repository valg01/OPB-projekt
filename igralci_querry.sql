---ZAVIHEK IGRALCI

--goli po igralcih
SELECT CASE
 WHEN p.given_name = 'not applicable' THEN p.family_name
 ELSE CONCAT(p.family_name || ' ', p.given_name) END
AS player_name, t.team_name AS team, count(DISTINCT g.goal_id) AS goals FROM players p
JOIN goals g ON p.player_id = g.player_id
JOIN player_appearances pa ON pa.player_id = p.player_id
JOIN teams t ON pa.team_id = t.team_id
GROUP BY player_name, t.team_name
ORDER BY goals desc

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

--rdečih in rumeni kartoni po igralcu

SELECT CASE
 WHEN p.given_name = 'not applicable' THEN p.family_name
 ELSE CONCAT(p.family_name || ' ', p.given_name) END as player_name,
 COUNT(CASE when yellow_card = True THEN booking_id END) as num_yellow,
 COUNT(CASE when red_card = True THEN booking_id END) as num_red,
 COUNT(CASE when second_yellow_card = True THEN booking_id END) as num_second_yellow,
 COUNT(CASE when b.sending_off = True THEN booking_id END) as num_sending_off from bookings b
JOIN players p on b.player_id = p.player_id
group by player_name
ORDER BY num_yellow desc, num_red desc, num_second_yellow desc, num_sending_off desc;

---nagrade po igralcih
SELECT  t.team_name,
case  WHEN p.given_name = 'not applicable' THEN p.family_name
 ELSE CONCAT(p.family_name || ' ', p.given_name) END as player_name,  count(Distinct award_id) AS num_of_awards FROM award_winners a
JOIN players p ON a.player_id = p.player_id
join player_appearances pa on p.player_id = pa.player_id
join teams t on pa.team_id = t.team_id
join confederations c on c.confederation_id = t.confederation_id
GROUP BY t.team_name, player_name 
order by num_of_awards DESC;

---goli_starost
SELECT case
 WHEN p.given_name = 'not applicable' then p.family_name
 ELSE CONCAT(p.family_name || ' ', p.given_name) END
AS player_name,
p.player_id,
count(DISTINCT g.goal_id) AS goals,
AVG(CAST(RIGHT(pa.tournament_id, 4) AS INT)  - EXTRACT('YEAR' FROM p.birth_date)) as average_age,
CASE
 WHEN average_age <= 24 then '<= 24 years' ELSE
 when average_age <= 31 then '< 24 <= 31 years' ELSE
 '> 31 years' end as age_group
FROM player_appearances pa
JOIN players p on p.player_id = pa.player_id
JOIN goals g ON p.player_id = g.player_id
GROUP BY p.player_id, player_name, age_group
ORDER BY GOALS desc

