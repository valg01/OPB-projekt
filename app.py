#!/usr/bin/python
# -*- encoding: utf-8 -*-

import bottle
from bottle import (
    get,
    post,
    run,
    request,
    template,
    redirect,
    response,
    url,
    static_file,
    route,
)
from Data.Database import Repo
from Data.Modeli import *
from Data.Services import AuthService
from functools import wraps
import os
import Data.auth_public as auth
import hashlib

import psycopg2, psycopg2.extensions, psycopg2.extras

from app_utils import RegistracijaUtils

from time import sleep

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
def preveriZnacko():
    if request.get_cookie("id", secret=SECRET_COOKIE_KEY):
        return 1
    return 0


@get("/views/images/<filepath:re:.*\.(jpg|png|gif|ico|svg)>")
def img(filepath):
    return static_file(filepath, root="views/images")


@route("/static/<filename:path>", name="static")
def static(filename):
    return static_file(filename, root=static_dir)


# zacetna stran
@get("/", name="index")
def index():
    znacka = preveriZnacko()
    return template("zacetna_stran.html", url=url, znacka=znacka)


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
        url=url,
        napaka=napaka,
        vloga=vloga,
        ime=ime,
        priimek=priimek,
        navijaska_drzava=navijaska_drzava,
        email=email,
    )


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

    hash_gesla = RegistracijaUtils.izracunaj_hash_gesla(geslo)

    try:
        print("Vnos v bazo...")
        cur.execute(
            """
            INSERT INTO uporabniki (ime, priimek, email, geslo, navijaska_drzava)
            VALUES (%s, %s, %s, %s, %s);
        """,
            (ime, priimek, email, hash_gesla, navijaska_drzava),
        )
        print("Vnos uspešen!")

        id_uporabnika = cur.fetchone()[0]
        conn.commit()
        print("Vnos uspešen!")
        response.set_cookie("id", id_uporabnika, path="/", secret=SECRET_COOKIE_KEY)
    except:
        response.set_cookie("sporocilo", "Napaka pri vnosu v bazo!")

    redirect(url("registracija_get"))
    return


if __name__ == "__main__":
    run(host="localhost", port=SERVER_PORT, reloader=RELOADER, debug=True)
