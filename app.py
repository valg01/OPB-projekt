#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
from functools import wraps

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

import psycopg2
import psycopg2.extensions
import psycopg2.extras

import Data.auth_public as auth
from app_utils import DBUtils, GeneralUtils, RegistracijaUtils
from bottleext import (
    get,
    post,
    redirect,
    request,
    response,
    route,
    run,
    static_file,
    template,
    url,
)
from Data.Database import Repo
from Data.Modeli import *
from Data.Services import AuthService
import pandas as pd

# problem s sumniki
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
conn = auth.connect()
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

folder_path = "views/graphs"

SERVER_PORT = os.environ.get("BOTTLE_PORT", 8080)
RELOADER = os.environ.get("BOTTLE_RELOADER", True)

SECRET_COOKIE_KEY = "37d445503ac1ed40e7b45775c0c3cd40"

static_dir = "./static"

pio.renderers.default = "notebook_connected"

repo = Repo()
auth = AuthService(repo)

"""@get('/graphs/<ime>.html')
def graf_assets(ime: str):
    return template(f'graphs/{ime}.html')"""


# za locitev med prijavo in odjavo
def preveri_znacko():
    """
    Checks if the user has a valid session cookie and returns 1 if they do, 0 otherwise.
    """
    if request.get_cookie("id", secret=SECRET_COOKIE_KEY):
        return 1
    return 0


def preveri_uporabnika():
    """
    Checks if the user has a valid session cookie and returns the user's ID if they do.
    If the user does not have a valid session cookie, redirects them to the login page.
    """
    id = request.get_cookie("id", secret=SECRET_COOKIE_KEY)
    if id:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute("SELECT id FROM uporabniki WHERE id = %s", [id])
            return DBUtils().dobi_prvi_rezultat(cur)
        except:
            redirect(url("prijava_get"))
    redirect(url("prijava_get"))


@get("/views/images/<filepath:re:.*\.(jpg|png|gif|ico|svg)>")
def img(filepath):
    """
    Returns the static file with the given filepath from the 'views/images' directory.

    Args:
        filepath (str): The filepath of the static file to be returned.

    Returns:
        The static file with the given filepath from the 'views/images' directory.
    """
    return static_file(filepath, root="views/images")


@route("/static/<filename:path>", name="static")
def static(filename):
    """
    Returns the static file with the given filename from the 'static' directory.

    Args:
        filename (str): The filename of the static file to be returned.

    Returns:
        The static file with the given filename from the 'static' directory.
    """
    return static_file(filename, root=static_dir)


# zacetna stran
@get("/", name="index")
def index():
    """
    Renders the home page template with the appropriate tag.

    Returns:
        The rendered home page template with the appropriate tag.
    """
    znacka = preveri_znacko()
    return template("zacetna_stran.html", znacka=znacka)


def dobi_vse_drzave(cur):
    """
    Returns a list of all team names from the 'teams' table.

    Args:
        cur (psycopg2.extensions.cursor): The cursor object used to execute the SQL query.

    Returns:
        A list of all team names from the 'teams' table.
    """
    cur.execute("SELECT team_name FROM teams")
    return GeneralUtils().flatten_list(cur.fetchall())


@get("/registracija", name="registracija_get")
def registracija_get():
    """
    Renders the registration page template with the appropriate tags and cookies.

    Returns:
        The rendered registration page template with the appropriate tags and cookies.
    """
    napaka = request.get_cookie("sporocilo")
    vloga = request.get_cookie("vloga", secret=SECRET_COOKIE_KEY)
    ime = request.get_cookie("ime", secret=SECRET_COOKIE_KEY)
    priimek = request.get_cookie("priimek", secret=SECRET_COOKIE_KEY)
    email = request.get_cookie("email", secret=SECRET_COOKIE_KEY)
    navijaska_drzava = request.get_cookie("navijaska_drzava")
    return template(
        "registracija.html",
        napaka=napaka,
        vloga=vloga,
        ime=ime,
        priimek=priimek,
        navijaska_drzava=navijaska_drzava,
        email=email,
        vse_mozne_drzave=dobi_vse_drzave(cur),
    )


# TODO (Val): Posodobi ER diagram s tabelo uporabniki
@post("/registracija", name="registracija_post")
def registracija_post():
    """
    Handles the registration form submission by validating the input data and inserting a new user into the database.

    Returns:
        Redirects the user to the appropriate page based on the success or failure of the registration process.
    """
    vloga = request.forms.vloga  # type: ignore
    ime = request.forms.ime  # type: ignore
    priimek = request.forms.priimek  # type: ignore
    email = request.forms.email  # type: ignore
    geslo = request.forms.geslo  # type: ignore
    geslo2 = request.forms.geslo2  # type: ignore
    navijaska_drzava = request.forms.navijaska_drzava  # type: ignore

    registracija_ok_bool, msg = RegistracijaUtils().registracija_ok_q(
        geslo=geslo, ponovljeno_geslo=geslo2, email=email, cur=cur
    )

    if not registracija_ok_bool:
        response.set_cookie("sporocilo", msg)  # , secret=SECRET_COOKIE_KEY, path="/")
        # imamo napako, nastavimo piskotke in preusmerimo
        response.set_cookie("ime", ime, path="/", secret=SECRET_COOKIE_KEY)
        response.set_cookie("priimek", priimek, path="/", secret=SECRET_COOKIE_KEY)
        response.set_cookie("vloga", vloga, path="/", secret=SECRET_COOKIE_KEY)
        response.set_cookie(
            "navijaska_drzava", navijaska_drzava, path="/", secret=SECRET_COOKIE_KEY
        )
        response.set_cookie("email", email, path="/", secret=SECRET_COOKIE_KEY)
        redirect(url("about"))

    hash_gesla = DBUtils.izracunaj_hash_gesla(geslo)

    try:
        cur.execute(
            "INSERT INTO uporabniki (ime, priimek, email, geslo, navijaska_drzava, vloga) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (ime, priimek, email, hash_gesla, navijaska_drzava, vloga),
        )
        id_uporabnika = DBUtils().dobi_prvi_rezultat(cur)
        conn.commit()

        response.set_cookie("id", id_uporabnika, path="/", secret=SECRET_COOKIE_KEY)
    except IndexError:
        response.set_cookie("sporocilo", "Napaka pri vnosu v bazo!")

    response.delete_cookie("sporocilo")
    redirect(url("uporabnik_get"))


@get("/prijava")
def prijava_get():
    """
    Renders the login page template with an optional error message.

    Returns:
        The rendered login page template with an optional error message.
    """
    napaka = request.get_cookie("sporocilo")
    return template("prijava.html", naslov="Prijava", napaka=napaka)


@post("/prijava")
def prijava_post():
    """
    Authenticates the user by checking their email and password against the database.
    If the email or password is incorrect, sets a cookie with an error message and redirects to the login page.
    If the email and password are correct, sets a cookie with the user's ID and redirects to the user page.

    Returns:
        None
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    email = request.forms.email  # type: ignore
    geslo = request.forms.geslo  # type: ignore
    try:
        cur.execute("SELECT geslo FROM uporabniki WHERE email = %s", [email])
        hash_baza = DBUtils().dobi_prvi_rezultat(cur)
    except:
        response.set_cookie("sporocilo", "Elektronski naslov ne obstaja!")
        redirect(url("prijava_get"))
        return

    if DBUtils.izracunaj_hash_gesla(geslo) != hash_baza:
        response.set_cookie(
            "sporocilo",
            "Ob danem elektronskem naslovu niste zapisali ustreznega gesla!",
        )
        redirect(url("prijava_get"))

    cur.execute("SELECT id FROM uporabniki WHERE email = %s", [email])
    id_uporabnika = DBUtils().dobi_prvi_rezultat(cur)
    response.set_cookie("id", id_uporabnika, secret=SECRET_COOKIE_KEY, path="/")
    response.delete_cookie("sporocilo")
    redirect(url("about"))


def pridobi_razpolozljive_drzave(cur, id_uporabnika):
    """
    Retrieves a list of available teams that the user has not yet selected.

    Args:
        cur: The database cursor.
        id_uporabnika: The ID of the user.

    Returns:
        A list of available teams that the user has not yet selected.
    """
    cur.execute(
        f"""SELECT t.team_name 
            FROM teams t
            WHERE NOT EXISTS (
                SELECT 1 
                FROM ekipe_uporabnika eu 
                WHERE eu.team_name = t.team_name AND eu.user_id = {id_uporabnika}
            )
        """
    )
    return GeneralUtils().flatten_list(cur.fetchall())


def pridobi_ze_izbrane_drzave(cur, id_uporabnika):
    """
    Retrieves a list of teams that the user has already selected.

    Args:
        cur: The database cursor.
        id_uporabnika: The ID of the user.

    Returns:
        A list of teams that the user has already selected.
    """
    cur.execute(
        f"SELECT team_name FROM ekipe_uporabnika WHERE user_id = {id_uporabnika}"
    )
    return GeneralUtils().flatten_list(cur.fetchall())


# TODO (Val): Posodobi ER diagram s tabelo ekipe_uporabnika
@get("/uporabnik")
def uporabnik_get():
    """
    Retrieves the current user's information and displays it on the user profile page.

    Returns:
        A rendered HTML template of the user profile page.
    """
    # TODO (Val): Predstavi stanje uporabnika
    id_uporabnika = preveri_uporabnika()
    znacka = preveri_znacko()
    napaka = request.get_cookie("sporocilo")
    razpolozljive_drzave = pridobi_razpolozljive_drzave(cur, id_uporabnika)
    ze_izbrane_drzave = pridobi_ze_izbrane_drzave(cur, id_uporabnika)
    return template(
        "uporabnik.html",
        razpolozljive_drzave=razpolozljive_drzave,
        napaka=napaka,
        znacka=znacka,
        ze_izbrane_drzave=ze_izbrane_drzave,
    )


def dodaj_drzavo(cur, id_uporabnika, ime_dodane_drzave):
    """
    Adds a selected team to the user's list of selected teams.

    Args:
        cur: The database cursor.
        id_uporabnika: The ID of the user.
        ime_dodane_drzave: The name of the team to be added.

    Returns:
        None.
    """
    cur.execute(
        f"INSERT INTO ekipe_uporabnika (team_name, user_id) VALUES ('{ime_dodane_drzave}', {id_uporabnika})"
    )
    conn.commit()
    return


def odstrani_drzavo(cur, id_uporabnika, ime_drzave_za_odstraniti):
    """
    Removes a selected team from the user's list of selected teams.

    Args:
        cur: The database cursor.
        id_uporabnika: The ID of the user.
        ime_drzave_za_odstraniti: The name of the team to be removed.

    Returns:
        None.
    """
    cur.execute(
        f"DELETE FROM ekipe_uporabnika WHERE team_name = '{ime_drzave_za_odstraniti}' AND user_id = {id_uporabnika}"
    )
    conn.commit()
    return


@post("/uporabnik/dodaj")
def uporabnik_post_dodaj_drzavo():
    """
    Adds a selected team to the user's list of selected teams.

    Args:
        None.

    Returns:
        None.
    """
    id_uporabnika = preveri_uporabnika()
    ime_dodane_drzave = request.forms.ime_dodane_drzave  # type: ignore
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if ime_dodane_drzave != "":
        dodaj_drzavo(cur, id_uporabnika, ime_dodane_drzave)
    redirect(url("uporabnik_get"))


@post("/uporabnik/dodaj_vse")
def uporabnik_post_dodaj_vse_drzave():
    """
    Adds all available teams to the user's list of selected teams.

    Args:
        None.

    Returns:
        None.
    """
    id_uporabnika = preveri_uporabnika()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    razpolozljive_drzave = pridobi_razpolozljive_drzave(cur, id_uporabnika)

    for drzava in razpolozljive_drzave:
        dodaj_drzavo(cur, id_uporabnika, drzava)

    redirect(url("uporabnik_get"))


@post("/uporabnik/odstrani")
def uporabnik_post_odstrani_drzavo():
    """
    Removes a selected team from the user's list of selected teams.

    Args:
        None.

    Returns:
        None.
    """
    id_uporabnika = preveri_uporabnika()
    ime_drzave_za_odstraniti = request.forms.ime_drzave_za_odstraniti  # type: ignore
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if ime_drzave_za_odstraniti != "":
        try:
            odstrani_drzavo(cur, id_uporabnika, ime_drzave_za_odstraniti)
        except:
            response.set_cookie("sporocilo", "Napaka pri vnosu v bazo!")
    redirect(url("uporabnik_get"))


@post("/uporabnik/odstrani_vse")
def uporabnik_post_odstrani_vse_drzave():
    """
    Removes all selected teams from the user's list of selected teams.

    Args:
        None.

    Returns:
        None.
    """
    id_uporabnika = preveri_uporabnika()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(
        f"DELETE FROM ekipe_uporabnika WHERE user_id = {id_uporabnika}"
    )
    conn.commit()

    redirect(url("uporabnik_get"))


@get("/about")
def about():
    """
    Renders the about page of the platform.

    Args:
        None.

    Returns:
        A rendered HTML template of the about page.
    """
    znacka = preveri_znacko()
    return template("about.html", naslov="O platformi", znacka=znacka)


@get("/odjava")
def odjava():
    """
    Logs out the user by deleting all cookies related to the user's session.

    Args:
        None.

    Returns:
        None.
    """
    response.delete_cookie("id")
    response.delete_cookie("vloga")
    response.delete_cookie("navijaska_drzava")
    response.delete_cookie("sporocilo")
    response.delete_cookie("ime")
    response.delete_cookie("priimek")
    response.delete_cookie("email")
    redirect(url("index"))


@get("/hall_of_fame")
def hall_of_fame():
    """
    Renders the hall of fame page of the platform.

    Args:
        None.

    Returns:
        A rendered HTML template of the hall of fame page.
    """
    znacka = preveri_znacko()
    return template("hall_of_fame.html", naslov="Hall of Fame", znacka=znacka)


@get("/turnirji")
def turnirji():
    """
    Renders the statistics page for teams.

    Args:
        None.

    Returns:
        A rendered HTML template of the statistics page for teams.
    """
    znacka = preveri_znacko()
    return template("turnirji.html", naslov="Turnirji", znacka=znacka)


@get("/drzave")
def drzave():
    """
    Renders the statistics page for teams.

    Args:
        None.

    Returns:
        A rendered HTML template of the statistics page for teams.
    """
    znacka = preveri_znacko()
    return template("drzave.html", naslov="Drzave", znacka=znacka)


@get("/igralci")
def igralci():
    """
    Renders the statistics page for teams.

    Args:
        None.

    Returns:
        A rendered HTML template of the statistics page for teams.
    """
    znacka = preveri_znacko()
    return template("igralci.html", naslov="Igralci", znacka=znacka)


@get("/profil")
def profil_get():
    """
    Renders the profile page of the user.

    Args:
        None.

    Returns:
        A rendered HTML template of the profile page of the user.
    """
    id_uporabnika = preveri_uporabnika()
    znacka = preveri_znacko()
    cur.execute(f"SELECT * FROM uporabniki WHERE id = {id_uporabnika}")
    napaka = request.get_cookie("sporocilo")
    [id, ime, priimek, email, hash_gesla, navijaska_drzava, vloga] = list(cur.fetchone())  # type: ignore
    return template(
        "profil.html",
        napaka=napaka,
        naslov="Podatki uporabnika",
        znacka=znacka,
        ime=ime,
        priimek=priimek,
        email=email,
        navijaska_drzava=navijaska_drzava,
        vloga=vloga,
    )

@post('/profil')
def profil_post():
    id_uporabnika = preveri_uporabnika()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    staro_geslo = request.forms.geslo_staro # type: ignore
    novo_geslo1 = request.forms.geslo1 # type: ignore
    novo_geslo2 = request.forms.geslo2 # type: ignore
    cur.execute("SELECT geslo FROM uporabniki WHERE id = %s", [id_uporabnika])
    hash_geslo = DBUtils().dobi_prvi_rezultat(cur)
    if DBUtils.izracunaj_hash_gesla(staro_geslo) != hash_geslo:
        response.set_cookie("sporocilo", 'Staro geslo je napacno!')
        redirect(url('profil_get'))
    elif len(novo_geslo1) < 4:
        response.set_cookie("sporocilo", 'Novo geslo mora imeti vsaj 4 znake!')
        redirect(url('profil_get'))
    elif novo_geslo1 != novo_geslo2:
        response.set_cookie("sporocilo", 'Gesli se ne ujemata!')
        redirect(url('profil_get'))
    else:
        novo_geslo = DBUtils.izracunaj_hash_gesla(novo_geslo1)  
        cur.execute("UPDATE uporabniki SET geslo = %s WHERE id = %s", [novo_geslo, id_uporabnika])
        conn.commit()
        response.set_cookie("sporocilo", 'Uspesno')
        response.delete_cookie("sporocilo")
        redirect(url('profil_get'))

@get("/wins")
def wins():
    return template(f"graphs/top_wins.html")


@get("/app")
def app():
    return template(f"graphs/top_app.html")


@get("/goals")
def goals():
    return template(f"graphs/top_goals.html")


@get("/cs")
def cs():
    return template(f"graphs/top_cs.html")


def join_countries(array):
    joined_values = ', '.join(["'" + value + "'" for value in array])
    return joined_values 


###########turnirji:
@get("/red_cards")
def rc():
    uporabnik_id = preveri_uporabnika()
    ekipe = pridobi_ze_izbrane_drzave(cur, uporabnik_id)
    if len(ekipe) > 0:
        drzave = join_countries(ekipe)
        red_cards = f"""select left(t.tournament_name, 4) AS tournament, count(b.booking_id) AS nm_bookings FROM bookings b
        JOIN tournaments t ON t.tournament_id = b.tournament_id
        left join player_appearances pa on pa.player_id = b.player_id
        left join teams te on pa.team_id = te.team_id
        where te.team_name in ({drzave})
        GROUP BY tournament_name, b.red_card
        HAVING b.red_card = 'True'
        ORDER BY tournament_name;"""
    else:
        red_cards = """select left(t.tournament_name, 4) AS tournament, count(b.booking_id) AS nm_bookings FROM bookings b
        JOIN tournaments t ON t.tournament_id = b.tournament_id
        left join player_appearances pa on pa.player_id = b.player_id
        left join teams te on pa.team_id = te.team_id
        GROUP BY tournament_name, b.red_card
        HAVING b.red_card = 'True'
        ORDER BY tournament_name;"""
    
    df1 = pd.read_sql_query(red_cards, conn)

    fig1 = go.Figure()

    fig1.add_trace(
        go.Scatter(
            x=df1["tournament"],
            y=df1["nm_bookings"],
            mode="lines",
            name="Line",
            line=dict(color="red"),
        )
    )

    fig1.update_layout(
        title="Number of Red Cards per Tournament",
        xaxis_title="Year",
        yaxis_title="Number of red cards",
    )

    fig1.update_layout(
        margin=dict(l=0,r=0,b=0,t=30),
        paper_bgcolor = "#C5C6D0"
    )

    file_path1 = f"{folder_path}/red_cards.html"
    fig1.write_html(file_path1, include_plotlyjs="cdn")
    return template(f"graphs/red_cards.html")


@get("/goals_tour")
def goals_t():
    goals_tournaments = """
    SELECT t.tournament_name, count(g.goal_id) AS numOfGoals FROM GOALS g
    JOIN tournaments t ON t.tournament_id = g.tournament_id
    GROUP BY t.tournament_name
    ORDER BY t.tournament_name ASC;
    """

    df2 = pd.read_sql_query(goals_tournaments,conn)

    fig2 = go.Figure()

    fig2.add_trace(
        go.Pie(
            labels=df2["tournament_name"],
            values=df2["numofgoals"],
            title= "Number of Goals per Tournament",
            hole= 0.75
        )
    )

    fig2.update_layout(
        margin=dict(l=0,r=0,b=0,t=30),
        paper_bgcolor = "#C5C6D0"
    )

    file_path2 = f"{folder_path}/goals_tour.html"
    fig2.write_html(file_path2, include_plotlyjs="cdn")
    return template(f"graphs/goals_tour.html")


@get("/goals_scored_in")
def goals_in():
    uporabnik_id = preveri_uporabnika()
    ekipe = pridobi_ze_izbrane_drzave(cur, uporabnik_id)
    if len(ekipe) > 0:
        drzave = join_countries(ekipe)
        goals_stadium_country = f"""SELECT s.stadium_name as stadium, s.city_name as city, s.country_name as country, COUNT(DISTINCT g.goal_id) as numOfGoals
        from stadiums s
        join matches m on m.stadium_id = s.stadium_id
        JOIN goals g on g.match_id = m.match_id
        left join player_appearances pa on pa.player_id = g.player_id
        left join teams t on t.team_id = pa.team_id
        where t.team_name in ({drzave})
        GROUP BY s.stadium_name, s.city_name, s.country_name
        ORDER BY numOfGoals DESC ;
        """
    else:
        goals_stadium_country = """SELECT s.stadium_name as stadium, s.city_name as city, s.country_name as country, COUNT(DISTINCT g.goal_id) as numOfGoals
        from stadiums s
        join matches m on m.stadium_id = s.stadium_id
        JOIN goals g on g.match_id = m.match_id
        left join player_appearances pa on pa.player_id = g.player_id
        left join teams t on t.team_id = pa.team_id
        GROUP BY s.stadium_name, s.city_name, s.country_name
        ORDER BY numOfGoals DESC ;
        """
    df3 = pd.read_sql_query(goals_stadium_country, conn)

    fig3 = px.treemap(
            df3,
            path=["country", "city"],
            values=df3["numofgoals"]
        )

    fig3.update_layout(
        title="Goals scored in city and country"
    )

    fig3.update_layout(
        margin=dict(l=0,r=0,b=0,t=30),
        paper_bgcolor = "#C5C6D0"
    )

    file_path3 = f"{folder_path}/goals_country.html"
    fig3.write_html(file_path3, include_plotlyjs="cdn")
    return template(f"graphs/goals_country.html")


@get("/matches_tour")
def matches_tour():
    matches_tournament = """
    SELECT t.tournament_name, count(m.match_id) as numOfMatches from matches m
    join tournaments t on t.tournament_id = m.tournament_id
    GROUP BY t.tournament_name
    ORDER BY t.tournament_name;
    """

    df4 = pd.read_sql_query(matches_tournament, conn)

    fig4 = go.Figure()

    fig4.add_trace(
        go.Bar(
            y=df4["tournament_name"],
            x=df4["numofmatches"],
            orientation="h"
        )
    )
    fig4.update_layout(
        title = "Matches by tournament"
    )
    fig4.update_layout(
        margin=dict(l=0,r=0,b=0,t=30),
        paper_bgcolor = "#C5C6D0"
    )
    file_path4 = f"{folder_path}/matches_tour.html"
    fig4.write_html(file_path4, include_plotlyjs="cdn")
    return template(f"graphs/matches_tour.html")


#######Drzave
@get("/tour_c")
def tour_c():
    uporabnik_id = preveri_uporabnika()
    ekipe = pridobi_ze_izbrane_drzave(cur, uporabnik_id)
    if len(ekipe) > 0:
        drzave = join_countries(ekipe)
        tournament_country = f"""SELECT --c.confederation_code as ConfederationCode
        c.confederation_name as ConfederationName
        , tour.host_country
        , COUNT(DISTINCT tournament_id) as num
        from tournaments tour
        join teams t on t.team_name = tour.host_country
        join confederations c on c.confederation_id = t.confederation_id
        WHERE t.team_name in ({drzave})
        group by ConfederationName, tour.host_country;
        """
    else:
        tournament_country = """SELECT --c.confederation_code as ConfederationCode
        c.confederation_name as ConfederationName
        , tour.host_country
        , COUNT(DISTINCT tournament_id) as num
        from tournaments tour
        join teams t on t.team_name = tour.host_country
        join confederations c on c.confederation_id = t.confederation_id
        group by ConfederationName, tour.host_country;
        """
    
    df1 = pd.read_sql_query(tournament_country, conn)

    fig1 = px.treemap(df1, path=["confederationname", "host_country"], values=df1["num"])

    fig1.update_layout(
        title="Number of Tournaments per Confederation and Country",
    )

    fig1.update_layout(
        margin=dict(l=0,r=0,b=0,t=30),
        paper_bgcolor = "#C5C6D0"
    )

    file_path1 = f"{folder_path}/tour_country.html"
    fig1.write_html(file_path1, include_plotlyjs="cdn")
    return template(f"graphs/tour_country.html")


@get("/awards_country")
def award_country():
    uporabnik_id = preveri_uporabnika()
    ekipe = pridobi_ze_izbrane_drzave(cur, uporabnik_id)
    if len(ekipe) > 0:
        drzave = join_countries(ekipe)
        awards_country = f"""SELECT  t.team_name,
        -- c.confederation_code,
        award_name, count(award_id) AS num_of_awards FROM award_winners a
        left join v_player_team pt on pt.player_id = a.player_id
        LEFT join teams t on pt.team_id = t.team_id
        LEFT join confederations c on c.confederation_id = t.confederation_id
        WHERE t.team_name in ({drzave})
        GROUP BY t.team_name, c.confederation_code, a.award_name 
        order by num_of_awards desc, award_name DESC;
        """
    else:
        awards_country = """SELECT  t.team_name,
        -- c.confederation_code,
        award_name, count(award_id) AS num_of_awards FROM award_winners a
        left join v_player_team pt on pt.player_id = a.player_id
        LEFT join teams t on pt.team_id = t.team_id
        join confederations c on c.confederation_id = t.confederation_id
        GROUP BY t.team_name, c.confederation_code, a.award_name 
        order by num_of_awards desc, award_name DESC;
        """
    df2 = pd.read_sql_query(awards_country, conn)
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
        xaxis=dict(tickangle=45)

    )
    fig2.update_layout(
        margin=dict(l=0,r=0,b=0,t=30),
        paper_bgcolor = "#C5C6D0"
    )

    file_path2 = f"{folder_path}/awards_c.html"
    fig2.write_html(file_path2, include_plotlyjs="cdn")
    return template(f"graphs/awards_c.html")


@get("/age_tournament")
def age_t():
    uporabnik_id = preveri_uporabnika()
    ekipe = pridobi_ze_izbrane_drzave(cur, uporabnik_id)
    if len(ekipe) > 0:
        drzave = join_countries(ekipe)
        age_country_tournament = f"""select tournament_name, team_name, AVG(age) as average_age
        from players_age
        WHERE team_name in ({drzave})
        GROUP BY tournament_name, team_name
        ORDER BY tournament_name ASC, average_age ASC;
        """
    else:
        age_country_tournament = """select tournament_name, team_name, AVG(age) as average_age
        from players_age
        GROUP BY tournament_name, team_name
        ORDER BY tournament_name ASC, average_age ASC;
        """
    df3 = pd.read_sql_query(age_country_tournament, conn)

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

    fig3.update_layout(
        margin=dict(l=0,r=0,b=0,t=30),
        paper_bgcolor = "#C5C6D0"
    )

    file_path3 = f"{folder_path}/age_t.html"
    fig3.write_html(file_path3, include_plotlyjs="cdn")     
    return template(f"graphs/age_t.html")


@get("/goals_country")
def goals_country():
    uporabnik_id = preveri_uporabnika()
    ekipe = pridobi_ze_izbrane_drzave(cur, uporabnik_id)
    if len(ekipe) > 0:
        drzave = join_countries(ekipe)
        goals_countries = f"""SELECT  t.team_name AS team
        , COUNT(DISTINCT g.goal_id) as NumberOfGoals FROM players p
        JOIN goals g ON p.player_id = g.player_id
        JOIN player_appearances pa ON pa.player_id = p.player_id
        JOIN teams t ON pa.team_id = t.team_id
        WHERE t.team_name in ({drzave})
        GROUP BY  t.team_name
        ORDER BY NumberOfGoals desc;
        """
    else:
        goals_countries = """SELECT  t.team_name AS team
        , COUNT(DISTINCT g.goal_id) as NumberOfGoals FROM players p
        JOIN goals g ON p.player_id = g.player_id
        JOIN player_appearances pa ON pa.player_id = p.player_id
        JOIN teams t ON pa.team_id = t.team_id
        GROUP BY  t.team_name
        ORDER BY NumberOfGoals desc;
        """
    df4 = pd.read_sql_query(goals_countries, conn)

    fig4 = go.Figure()

    fig4.add_trace(
        go.Pie(
            labels = df4["team"],
            values = df4["numberofgoals"],
            textinfo= "none"
        )
    )

    fig4.update_layout(
        showlegend = True,
        title = "Goals Scored per Country"
    )

    fig4.update_layout(
        margin=dict(l=0,r=0,b=0,t=30),
        paper_bgcolor = "#C5C6D0"
    )

    file_path4 = f"{folder_path}/goals_c.html"
    fig4.write_html(file_path4, include_plotlyjs="cdn")
    return template(f"graphs/goals_c.html")


@get("/position")
def position():
    uporabnik_id = preveri_uporabnika()
    ekipe = pridobi_ze_izbrane_drzave(cur, uporabnik_id)
    if len(ekipe) > 0:
        drzave = join_countries(ekipe)
        countires_position = f"""SELECT t.team_name as team,
        COUNT(CASE WHEN "position" = 1 then ts.team_id END) as winners,
        COUNT(CASE WHEN "position" = 2 then ts.team_id END) as runnerups,
        COUNT(CASE WHEN "position" = 3 then ts.team_id END) as third,
        COUNT(CASE WHEN "position" = 4 then ts.team_id END) as fourth
        FROM tournament_standings ts
        join teams t on t.team_id = ts.team_id
        where team_name in ({drzave})
        GROUP BY t.team_name
        order by winners desc, runnerups desc, third desc, fourth DESC, team asc;
        """
    else:
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
    df5 = pd.read_sql_query(countires_position, conn)

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
        showlegend=True,
        xaxis=dict(tickangle=45)

    )

    fig5.update_layout(
        margin=dict(l=0,r=0,b=0,t=30),
        paper_bgcolor = "#C5C6D0"
    )

    file_path5 = f"{folder_path}/position.html"
    fig5.write_html(file_path5, include_plotlyjs="cdn")
    return template(f"graphs/position.html")    


#####Igralci


@get("/goals_p")
def goals_p():
    uporabnik_id = preveri_uporabnika()
    ekipe = pridobi_ze_izbrane_drzave(cur, uporabnik_id)
    if len(ekipe) > 0:
        drzave = join_countries(ekipe)
        goals_players = f"""SELECT CASE
        WHEN p.given_name = 'not applicable' THEN p.family_name
        ELSE CONCAT(p.family_name || ' ', p.given_name) END
        AS player_name, t.team_name AS team, count(DISTINCT g.goal_id) AS goals FROM players p
        JOIN goals g ON p.player_id = g.player_id
        JOIN player_appearances pa ON pa.player_id = p.player_id
        JOIN teams t ON pa.team_id = t.team_id
        WHERE t.team_name in ({drzave})
        GROUP BY player_name, t.team_name
        ORDER BY goals desc
        LIMIT 150
        """
    else:
        goals_players = """SELECT CASE
        WHEN p.given_name = 'not applicable' THEN p.family_name
        ELSE CONCAT(p.family_name || ' ', p.given_name) END
        AS player_name, t.team_name AS team, count(DISTINCT g.goal_id) AS goals FROM players p
        JOIN goals g ON p.player_id = g.player_id
        JOIN player_appearances pa ON pa.player_id = p.player_id
        JOIN teams t ON pa.team_id = t.team_id
        GROUP BY player_name, t.team_name
        ORDER BY goals desc
        LIMIT 150
        """
    df1 = pd.read_sql_query(goals_players, conn)

    fig1 = go.Figure()

    fig1.add_trace(
        go.Bar(
            x = df1["player_name"],
            y = df1["goals"],
            width = 1.2,
            marker=dict(color=df1["goals"], colorscale='Viridis')
        )
    )

    fig1.update_layout(
        margin=dict(l=0,r=0,b=0,t=30),
        paper_bgcolor = "#C5C6D0",
        title = "Top 150 Players per Goals",
        xaxis=dict(tickangle=45)
    )

    file_path1 = f"{folder_path}/goals_p.html"
    fig1.write_html(file_path1, include_plotlyjs="cdn")
    return template(f"graphs/goals_p.html")


@get("/bookings_p")
def bookings_p():
    uporabnik_id = preveri_uporabnika()
    ekipe = pridobi_ze_izbrane_drzave(cur, uporabnik_id)
    if len(ekipe) > 0:
        drzave = join_countries(ekipe)
        bookings_players = f"""SELECT CASE
        WHEN p.given_name = 'not applicable' THEN p.family_name
        ELSE CONCAT(p.family_name || ' ', p.given_name) END as player_name,
        COUNT(CASE when yellow_card = True THEN booking_id END) as num_yellow,
        COUNT(CASE when red_card = True THEN booking_id END) as num_red,
        COUNT(CASE when second_yellow_card = True THEN booking_id END) as num_second_yellow,
        COUNT(CASE when b.sending_off = True THEN booking_id END) as num_sending_off from bookings b
        JOIN players p on b.player_id = p.player_id
        left join player_appearances pa on pa.player_id = b.player_id and pa.match_id = b.match_id
        left join teams te on pa.team_id = te.team_id
        WHERE te.team_name in ({drzave})
        group by player_name
        ORDER BY num_yellow desc, num_red desc, num_second_yellow desc, num_sending_off desc
        LIMIT 100;
        """
    else:
        bookings_players = """SELECT CASE
        WHEN p.given_name = 'not applicable' THEN p.family_name
        ELSE CONCAT(p.family_name || ' ', p.given_name) END as player_name,
        COUNT(CASE when yellow_card = True THEN booking_id END) as num_yellow,
        COUNT(CASE when red_card = True THEN booking_id END) as num_red,
        COUNT(CASE when second_yellow_card = True THEN booking_id END) as num_second_yellow,
        COUNT(CASE when b.sending_off = True THEN booking_id END) as num_sending_off from bookings b
        JOIN players p on b.player_id = p.player_id
        left join player_appearances pa on pa.player_id = b.player_id and pa.match_id = b.match_id
        left join teams te on pa.team_id = te.team_id
        group by player_name
        ORDER BY num_yellow desc, num_red desc, num_second_yellow desc, num_sending_off desc
        LIMIT 100;
        """

    df2 = pd.read_sql_query(bookings_players, conn)

    fig2 = go.Figure()

    fig2.add_trace(
        go.Bar(
            x = df2['player_name'],
            y = df2['num_yellow'],
            name='Yellow cards',
            width = 0.7
        )
    )

    fig2.add_trace(
        go.Bar(
            x = df2['player_name'],
            y = df2['num_red'],
            name='Red cards',
            base = df2['num_yellow'],
            width = 0.7
        )
    )

    fig2.add_trace(
        go.Bar(
            x = df2['player_name'],
            y = df2['num_second_yellow'],
            name='Second yellow cards',
            base = df2['num_yellow'] + df2['num_red'],
            width = 0.7
        )
    )

    fig2.add_trace(
        go.Line(
            x = df2['player_name'],
            y = df2['num_sending_off'],
            name = "Sending-offs",
            line=dict(color="cyan"),
            fill = "tonexty"
        )
    )

    fig2.update_layout(
        title = 'Top 100 Players per Booking',
        xaxis_title="Player",
        yaxis_title="Number of Bookings",
        barmode='stack', 
        showlegend=True,
        xaxis=dict(tickangle=45)
    )

    fig2.update_layout(
        margin=dict(l=0,r=0,b=0,t=30),
        paper_bgcolor = "#C5C6D0"
    )

    file_path2 = f"{folder_path}/bookings_p.html"
    fig2.write_html(file_path2, include_plotlyjs="cdn")
    return template(f"graphs/bookings_p.html")


@get("/awards_p")
def awards_p():
    uporabnik_id = preveri_uporabnika()
    ekipe = pridobi_ze_izbrane_drzave(cur, uporabnik_id)
    if len(ekipe) > 0:
        drzave = join_countries(ekipe)
        players_awards = f"""
        SELECT  c.confederation_code, t.team_name,
        case  WHEN p.given_name = 'not applicable' THEN p.family_name
        ELSE CONCAT(p.family_name || ' ', p.given_name) END as player_name,  count(Distinct award_id) AS num_of_awards FROM award_winners a
        JOIN players p ON a.player_id = p.player_id
        join player_appearances pa on p.player_id = pa.player_id
        join teams t on pa.team_id = t.team_id
        join confederations c on c.confederation_id = t.confederation_id
        where t.team_name in ({drzave})
        GROUP BY t.team_name, player_name, c.confederation_code
        order by num_of_awards DESC;
        """
    else:
        players_awards = """
        SELECT  c.confederation_code, t.team_name,
        case  WHEN p.given_name = 'not applicable' THEN p.family_name
        ELSE CONCAT(p.family_name || ' ', p.given_name) END as player_name,  count(Distinct award_id) AS num_of_awards FROM award_winners a
        JOIN players p ON a.player_id = p.player_id
        join player_appearances pa on p.player_id = pa.player_id
        join teams t on pa.team_id = t.team_id
        join confederations c on c.confederation_id = t.confederation_id
        GROUP BY t.team_name, player_name, c.confederation_code
        order by num_of_awards DESC;
        """
    df3 = pd.read_sql_query(players_awards, conn)

    fig3 = px.treemap(df3, path=["confederation_code","team_name", "player_name"], values=df3["num_of_awards"])

    fig3.update_layout(
        margin=dict(l=0,r=0,b=0,t=30),
        paper_bgcolor = "#C5C6D0",
        title = "Awards by Confederation, Teams and Players"
    )

    file_path3 = f"{folder_path}/awards_p.html"
    fig3.write_html(file_path3, include_plotlyjs="cdn")
    return template(f"graphs/awards_p.html")


@get("/scatter_p")
def scatter_p():
    uporabnik_id = preveri_uporabnika()
    ekipe = pridobi_ze_izbrane_drzave(cur, uporabnik_id)
    if len(ekipe) > 0:
        drzave = join_countries(ekipe)
        age_goals = f"""SELECT case
        WHEN p.given_name = 'not applicable' then p.family_name
        ELSE CONCAT(p.family_name || ' ', p.given_name) END
        AS player_name,
        COUNT(DISTINCT pa.match_id) AS appearances,
        count(DISTINCT g.goal_id) AS goals,
        AVG(CAST(RIGHT(pa.tournament_id, 4) AS INT)  - EXTRACT('YEAR' FROM p.birth_date)) as average_age,
        CASE
        WHEN AVG(CAST(RIGHT(pa.tournament_id, 4) AS INT)  - EXTRACT('YEAR' FROM p.birth_date)) <= 24 then '<= 24 years' 
        when AVG(CAST(RIGHT(pa.tournament_id, 4) AS INT)  - EXTRACT('YEAR' FROM p.birth_date)) <= 31 then '< 24 <= 31 years'
        ELSE '> 31 years' END as age_group
        FROM player_appearances pa
        JOIN players p on p.player_id = pa.player_id
        left JOIN goals g ON pa.player_id = g.player_id and pa.match_id = g.match_id
        left join teams t on t.team_id = pa.team_id
        WHERE t.team_name in ({drzave})
        GROUP BY  player_name
        ORDER BY age_group ASC, GOALS desc;
        """
    else:
        age_goals = """SELECT case
        WHEN p.given_name = 'not applicable' then p.family_name
        ELSE CONCAT(p.family_name || ' ', p.given_name) END
        AS player_name,
        COUNT(DISTINCT pa.match_id) AS appearances,
        count(DISTINCT g.goal_id) AS goals,
        AVG(CAST(RIGHT(pa.tournament_id, 4) AS INT)  - EXTRACT('YEAR' FROM p.birth_date)) as average_age,
        CASE
        WHEN AVG(CAST(RIGHT(pa.tournament_id, 4) AS INT)  - EXTRACT('YEAR' FROM p.birth_date)) <= 24 then '<= 24 years' 
        when AVG(CAST(RIGHT(pa.tournament_id, 4) AS INT)  - EXTRACT('YEAR' FROM p.birth_date)) <= 31 then '< 24 <= 31 years'
        ELSE '> 31 years' END as age_group
        FROM player_appearances pa
        JOIN players p on p.player_id = pa.player_id
        left JOIN goals g ON pa.player_id = g.player_id and pa.match_id = g.match_id
        left join teams t on t.team_id = pa.team_id
        GROUP BY  player_name
        ORDER BY age_group ASC, GOALS desc;
        """ 
    df4 = pd.read_sql_query(age_goals, conn)

    fig4 = px.scatter(df4, x = "average_age", y = "appearances",  trendline="ols",color = "goals", size="goals", hover_data="player_name")

    fig4.update_layout(
        margin=dict(l=0,r=0,b=0,t=30),
        paper_bgcolor = "#C5C6D0",
        title = "Goals Scored by Average Age and Appearances"
    )

    file_path4 = f"{folder_path}/scatter_p.html"
    fig4.write_html(file_path4, include_plotlyjs="cdn") 
    return template(f"graphs/scatter_p.html")


if __name__ == "__main__":
    run(host="localhost", port=int(SERVER_PORT), reloader=bool(RELOADER), debug=True)
