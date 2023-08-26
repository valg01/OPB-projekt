#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
from functools import wraps

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

# problem s šumniki
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
conn = auth.connect()
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

SERVER_PORT = os.environ.get("BOTTLE_PORT", 8080)
RELOADER = os.environ.get("BOTTLE_RELOADER", True)

SECRET_COOKIE_KEY = "37d445503ac1ed40e7b45775c0c3cd40"

static_dir = "./static"

repo = Repo()
auth = AuthService(repo)

"""@get('/graphs/<ime>.html')
def graf_assets(ime: str):
    return template(f'graphs/{ime}.html')"""


# za ločitev med prijavo in odjavo
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
        # imamo napako, nastavimo piškotke in preusmerimo
        response.set_cookie("ime", ime, path="/", secret=SECRET_COOKIE_KEY)
        response.set_cookie("priimek", priimek, path="/", secret=SECRET_COOKIE_KEY)
        response.set_cookie("vloga", vloga, path="/", secret=SECRET_COOKIE_KEY)
        response.set_cookie(
            "navijaska_drzava", navijaska_drzava, path="/", secret=SECRET_COOKIE_KEY
        )
        response.set_cookie("email", email, path="/", secret=SECRET_COOKIE_KEY)
        redirect(url("registracija_get"))

    hash_gesla = DBUtils.izracunaj_hash_gesla(geslo)

    try:
        cur.execute(
            "INSERT INTO uporabniki (ime, priimek, email, geslo, navijaska_drzava, vloga) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (ime, priimek, email, hash_gesla, navijaska_drzava, vloga),
        )
        id_uporabnika = DBUtils().dobi_prvi_rezultat(cur)
        conn.commit()

        print("Vnos uspešen!")
        response.set_cookie("id", id_uporabnika, path="/", secret=SECRET_COOKIE_KEY)
    except IndexError:
        response.set_cookie("sporocilo", "Napaka pri vnosu v bazo!")

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
    redirect(url("uporabnik_get"))


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
    print("Dodajam državo", ime_dodane_drzave)
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
    return template("drzave.html", naslov="Države", znacka=znacka)


@get("/statistike_ekip")
def statistike_ekip():
    """
    Renders the statistics page for teams.

    Args:
        None.

    Returns:
        A rendered HTML template of the statistics page for teams.
    """
    znacka = preveri_znacko()
    return template("statistike_ekip.html", naslov="Statistike ekip", znacka=znacka)


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
    return template("igralci.html", naslov="igralci", znacka=znacka)


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
        response.set_cookie("sporocilo", 'Staro geslo je napačno!')
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
def goals():
    return template(f"graphs/top_cs.html")


###########turnirji:
@get("/red_cards")
def rc():
    return template(f"graphs/red_cards.html")


@get("/goals_tour")
def goals_t():
    return template(f"graphs/goals_tour.html")


@get("/goals_scored_in")
def goals_in():
    return template(f"graphs/goals_country.html")


@get("/matches_tour")
def matches_tour():
    return template(f"graphs/matches_tour.html")


#######Države
@get("/tour_c")
def tour_c():
    return template(f"graphs/tour_country.html")


@get("/awards_country")
def award_country():
    return template(f"graphs/awards_c.html")


@get("/age_tournament")
def age_t():
    return template(f"graphs/age_t.html")


@get("/goals_country")
def goals_country():
    return template(f"graphs/goals_c.html")


@get("/position")
def position():
    return template(f"graphs/position.html")


#####Igralci


@get("/goals_p")
def goals_p():
    return template(f"graphs/goals_p.html")


@get("/bookings_p")
def bookings_p():
    return template(f"graphs/bookings_p.html")


@get("/awards_p")
def awards_p():
    return template(f"graphs/awards_p.html")


@get("/scatter_p")
def scatter_p():
    return template(f"graphs/scatter_p.html")


if __name__ == "__main__":
    run(host="localhost", port=int(SERVER_PORT), reloader=bool(RELOADER), debug=True)
