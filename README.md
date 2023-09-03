# Svetovna prvenstva v nogometu

Projekt, ki analizira podatke iz svetovnih prvenstev v nogometu v letih 1930-2022. Cilj tega projekta je zagotoviti organiziran in učinkovit način za shranjevanje in upravljanje podatkov, povezanih s tekmami nogometnega svetovnega prvenstva, ekipami, igralci in drugimi povezanimi informacijami, ter vse to predstaviti na spletnem vmesniku. Podatke sva uvozila iz [obstoječe podatkovne baze](https://github.com/jfjelstul/worldcup?fbclid=IwAR2ezFC64kBLC75OSXOg4iR_lhlddSlkgLrC-Y9Eh3A6-wpyasCd03UrwKg).

## Spletni dostop

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/valg01/Svetovna-prvenstva-v-nogometu/main)

## ER diagram
<img width="1230" alt="image" src="https://user-images.githubusercontent.com/82824154/230346357-85a50732-d205-40ca-bcaf-94098c841462.png">
## Struktura baze

Tu so naštete tabele, ki jih bova v najini bazi imela:
- **Award Winners** *(Tournament ID, award ID, player ID, Award Name)*
- **Bookings** *(Booking ID, Tournament ID, Match ID, Team ID, Player ID, Yellow Card, Red Card, Second Yellow Card, Sending Off, Minute Regulation, Match Period)*
- **Confederation** *(Confederation ID, Confederation Name, Confederation Code)*
- **Goals** *(Goal ID, Tournament ID, Match ID, Stage Name, Team ID, Player ID, Player Team ID, Minute Regulation, Match Period, Own Goal, Penalty)*
- **Group Standings** *(Tournament ID, Stage Number, Stage Name, Position, Team ID, Played, Wins, Draws, Losses, Goals For, Goals Against,Points, Advanced)*
- **Host Contries** *(Tournament ID, Tournament Name, Team ID, Performance)*
- **Matches** *(Tournament ID, Match ID, Match Name, Stage Name, Group Stage, Konckout Stage, Replayed, Replay, Match Date, Stadium ID, Home Team ID, Away Team ID, Score, Extra Time, Penalty Shootout, Score Penalties, Home Team Win, Away Team Win, Draw)*
- **Penalty Kicks** *(Penalty Kick ID, Tournament ID, Match ID, Stage Name, Team ID, Player ID, Converted)*
- **Player Appearances** *(Tournament ID, Match ID, Team ID, Player ID, Position Name, Position Code, Starter, Substitute, Captain)*
- **Players** *(Player ID, Family Name, Given Name, Birth Date, Goal Keeper, Defender, Midfielder, Forward, Count Tournaments, List Tournaments)*
- **Qualified Teams** *(Tournament ID, Team ID, Count Matches, Performance, Team Name, Team Code)*
- **Stadiums** *(Stadium ID, Stadium Name, City Name, Country Name, Stadium Capacity)*
- **Team Appearances** *(Tournament ID, Match ID, Match Name, Stage Name, Group Stage, Stadium ID, Team ID, Opponent ID, Home Team, Away Team, Goals For, Goals Against, Extra Time, Penalty Shootout, Penalties For, Penalities Against, Result, Win, Lose, Draw)*
- **Teams** *(Team ID, Team Name, Team Code, Confederation, Federation Name)*
- **Tournament Stadings** *(Tournament ID, Team ID, Position)*
- **Tournaments** *(Tournament ID, Tournament Name, Start Date, End Date, Host Country, Winner, Count Teams)*
