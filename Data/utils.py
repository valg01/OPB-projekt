
from numpy import dtype
import pandas as pd



TABLE_DATA = {
    "award_winners": {
        "tournament_id": "str",
        "award_id": "str",
        "player_id": "str",
        "award_name": "str"
    },
    "bookings": {
        "booking_id": "str",
        "tournament_id": "str",
        "match_id": "str",
        "team_id": "str",
        "player_id": "str",
        "yellow_card": "bool",
        "red_card": "bool",
        "second_yellow_card": "bool",
        "sending_off": "bool",
        "minute_regulation": "int",
        "match_period": "str"
    },
    "confederations": {
        "confederation_id": "str",
        "confederation_name": "str",
        "confederation_code": "str"
    },
    "goals": {
        "goal_id": "str",
        "tournament_id": "str",
        "match_id": "str",
        "stage_name": "str",
        "team_id": "str",
        "player_id": "str",
        "player_team_id": "str",
        "minute_regulation": "int",
        "match_period": "str",
        "own_goal": "bool",
        "penalty": "bool"
    },
    "group_standings": {
        "tournament_id": "str",
        "stage_number": "int",
        "stage_name": "str",
        "position": "int",
        "team_id": "str",
        "played": "int",
        "wins": "int",
        "draws": "int",
        "losses": "int",
        "goals_for": "int",
        "goals_against": "int",
        "points": "int",
        "advanced": "bool"
    },
    "host_countries": {
        "tournament_id": "str",
        "tournament_name": "str",
        "team_id": "str",
        "performance": "str"
    },
    "matches": {
        "tournament_id": "str",
        "match_id": "str",
        "match_name": "str",
        "stage_name": "str",
        "group_stage": "bool",
        "knockout_stage": "bool",
        "replayed": "bool",
        "replay": "bool",
        "match_date": "date",
        "stadium_id": "str",
        "home_team_id": "str",
        "away_team_id": "str",
        "score": "str",
        "extra_time": "str",
        "penalty_shootout": "bool",
        "score_penalties": "str",
        "home_team_win": "bool",
        "away_team_win": "bool",
        "draw": "bool"
    },
    "penalty_kicks": {
        "penalty_kick_id": "str",
        "tournament_id": "str",
        "match_id": "str",
        "stage_name": "str",
        "team_id": "str",
        "player_id": "str",
        "converted": "bool"
    },
    "player_appearances": {
        "tournament_id": "str",
        "match_id": "str",
        "team_id": "str",
        "player_id": "str",
        "position_name": "str",
        "position_code": "str",
        "starter": "bool",
        "substitute": "bool",
        "captain": "bool"
    },
    "players": {
        "player_id": "str",
        "family_name": "str",
        "given_name": "str",
        "birth_date": "date",
        "goal_keeper": "bool",
        "defender": "bool",
        "midfielder": "bool",
        "forward": "bool",
        "count_tournaments": "int",
        "list_tournaments": "str"
    },
    "qualified_teams": {
        "tournament_id": "str",
        "team_id": "str",
        "count_matches": "int",
        "performance": "str",
        "team_name": "str",
        "team_code": "str"
    },
    "stadiums": {
        "stadium_id": "str",
        "stadium_name": "str",
        "city_name": "str",
        "country_name": "str",
        "stadium_capacity": "int"
    },
    "team_appearances": {
        "tournament_id": "str",
        "match_id": "str",
        "match_name": "str",
        "stage_name": "str",
        "group_stage": "bool",
        "stadium_id": "str",
        "team_id": "str",
        "opponent_id": "str",
        "home_team": "bool",
        "away_team": "bool",
        "goals_for": "int",
        "goals_against": "int",
        "extra_time": "str",
        "penalty_shootout": "bool",
        "penalties_for": "int",
        "penalties_against": "int",
        "result": "str",
        "win": "bool",
        "lose": "bool",
        "draw": "bool"
    },
    "teams": {
        "team_id": "str",
        "team_name": "str",
        "team_code": "str",
        "confederation_id": "str",
        "federation_name": "str"
    },
    "tournament_standings": {
        "tournament_id": "str",
        "team_id": "str",
        "position": "int"
    },
    "tournaments": {
        "tournament_id": "str",
        "tournament_name": "str",
        "start_date": "date",
        "end_date": "date",
        "host_country": "str",
        "winner": "str",
        "count_teams": "int"
    }
}