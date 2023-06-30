#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
from functools import wraps

import psycopg2
import psycopg2.extensions
import psycopg2.extras

import Data.auth_public as auth
from app_utils import RegistracijaUtils, DBUtils, GeneralUtils
from bottleext import (
    get,
    post,
    redirect,
    request,
    response,
    route,
    run,
    static_file,
    url,
    template,
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


# za ločitev med prijavo in odjavo
def preveri_znacko():
    if request.get_cookie("id", secret=SECRET_COOKIE_KEY):
        return 1
    return 0


def preveri_uporabnika():
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
    return static_file(filepath, root="views/images")


@route("/static/<filename:path>", name="static")
def static(filename):
    return static_file(filename, root=static_dir)


# zacetna stran
@get("/", name="index")
def index():
    znacka = preveri_znacko()
    return template("zacetna_stran.html", znacka=znacka)


def dobi_vse_drzave(cur):
    cur.execute("SELECT team_name FROM teams")
    return GeneralUtils().flatten_list(cur.fetchall())


@get("/registracija", name="registracija_get")
def registracija_get():
    napaka = request.get_cookie("sporocilo")
    vloga = request.get_cookie("vloga")
    ime = request.get_cookie("ime")
    priimek = request.get_cookie("priimek")
    email = request.get_cookie("email", "_")
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
        # nastavi_sporocilo(msg)
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
        print("Vnos v bazo...")
        # TODO: Tukaj se zalomi
        cur.execute(
            "INSERT INTO uporabniki (ime, priimek, email, geslo, navijaska_drzava) VALUES (%s, %s, %s, %s, %s)",
            (ime, priimek, email, hash_gesla, navijaska_drzava),
        )
        print("Vnos uspešen!")

        id_uporabnika = DBUtils().dobi_prvi_rezultat(cur)
        conn.commit()
        print("Vnos uspešen!")
        response.set_cookie("id", id_uporabnika, path="/", secret=SECRET_COOKIE_KEY)
    except:
        response.set_cookie("sporocilo", "Napaka pri vnosu v bazo!")

    redirect(url("registracija_get"))
    return


@get("/prijava")
def prijava_get():
    napaka = request.get_cookie("sporocilo")
    return template("prijava.html", naslov="Prijava", napaka=napaka)


@post("/prijava")
def prijava_post():
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
    cur.execute(
        f"SELECT team_name FROM ekipe_uporabnika WHERE user_id = {id_uporabnika}"
    )
    return GeneralUtils().flatten_list(cur.fetchall())


# TODO (Val): Posodobi ER diagram s tabelo ekipe_uporabnika
@get("/uporabnik")
def uporabnik_get():
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
    cur.execute(
        f"INSERT INTO ekipe_uporabnika (team_name, user_id) VALUES ('{ime_dodane_drzave}', {id_uporabnika})"
    )
    conn.commit()
    return

def odstrani_drzavo(cur, id_uporabnika, ime_drzave_za_odstraniti):
    cur.execute(
        f"DELETE FROM ekipe_uporabnika WHERE team_name = '{ime_drzave_za_odstraniti}' AND user_id = {id_uporabnika}"
    )
    conn.commit()
    return

@post("/uporabnik")
def uporabnik_post():
    id_uporabnika = preveri_uporabnika()
    ime_dodane_drzave = request.forms.ime_dodane_drzave
    ime_drzave_za_odstraniti = request.forms.ime_drzave_za_odstraniti
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    error_msg = "Napaka pri vnosu v bazo!"

    if ime_dodane_drzave != "":
        try:
            dodaj_drzavo(cur, id_uporabnika, ime_dodane_drzave)
        except:
            response.set_cookie("sporocilo", error_msg)
    if ime_drzave_za_odstraniti != "":
        try:
            odstrani_drzavo(cur, id_uporabnika, ime_drzave_za_odstraniti)
        except:
            response.set_cookie("sporocilo", error_msg)

    redirect(url("uporabnik_get"))


@get('/about')
def about():
    znacka = preveri_znacko()
    return template("about.html", naslov='O platformi', znacka=znacka)

if __name__ == "__main__":
    run(host="localhost", port=int(SERVER_PORT), reloader=bool(RELOADER), debug=True)
