--ZAVIHEK Turnirji

---Rdeči kartoni po turnirjih

select
    left(t.tournament_name, 4) AS tournament,
    count(b.booking_id) AS nm_bookings
FROM bookings b
    JOIN tournaments t ON t.tournament_id = b.tournament_id
GROUP BY
    tournament_name,
    b.red_card
HAVING b.red_card = 'True'
ORDER BY tournament_name;

---Goli po turnirjih

SELECT
    t.tournament_name,
    count(g.goal_id) as numOfGoals
from GOALS g
    join tournaments t on t.tournament_id = g.tournament_id
GROUP BY t.tournament_name
ORDER BY t.tournament_name ASC;

---Tekme po turnirjih

SELECT
    t.tournament_name,
    count(m.match_id) as numOfMatches
from matches m
    join tournaments t on t.tournament_id = m.tournament_id
GROUP BY t.tournament_name
ORDER BY t.tournament_name;

-- goli po turnirjih in pozicijah

SELECT
    t.tournament_name as Tournament,
    COALESCE(
        sum(
            CASE
                WHEN p.goal_keeper THEN 1
                ELSE 0
            END
        )
    ) as goals_keeper,
    COALESCE(
        sum(
            CASE
                WHEN p.defender THEN 1
                ELSE 0
            END
        )
    ) as goals_defender,
    COALESCE(
        sum(
            CASE
                WHEN p.midfielder THEN 1
                ELSE 0
            END
        )
    ) as goals_midfielder,
    COALESCE(
        sum(
            CASE
                WHEN p.forward THEN 1
                ELSE 0
            END
        )
    ) as goals_forward,
    COUNT(DISTINCT g.goal_id) as NumberOfGoals
FROM tournaments t
    join goals g ON g.tournament_id = t.tournament_id
    join players p on p.player_id = g.player_id
GROUP BY tournament_name
order by NumberOfGoals desc;

--Tekme po stadionih in mestih z goli

SELECT
    s.stadium_name as stadium,
    s.city_name as city,
    s.country_name as country,
    COUNT(DISTINCT g.goal_id) as numOfGoals
from stadiums s
    join matches m on m.stadium_id = s.stadium_id
    JOIN goals g on g.match_id = m.match_id
GROUP BY
    s.stadium_name,
    s.city_name,
    s.country_name
ORDER BY numOfGoals asc;

--Leta ko so zmagali gostitelji

SELECT
    REPLACE(
        tournament_name,
        ' FIFA World Cup',
        ''
    ) as year,
    winner
FROM tournaments
where winner = host_country;