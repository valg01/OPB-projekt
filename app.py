#!/usr/bin/python
# -*- encoding: utf-8 -*-

import bottle
from bottle import get, post, run, request, template, redirect, response, url, static_file, route
from Data.Database import Repo
from Data.Modeli import *
from Data.Services import AuthService
from functools import wraps
import os
import Data.auth_public as auth
import hashlib

import psycopg2, psycopg2.extensions, psycopg2.extras

# problem s šumniki
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
conn = auth.connect()
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)

SECRET_COOKIE_KEY = "37d445503ac1ed40e7b45775c0c3cd40"

static_dir = "./static"

"""def include_file(filename):
    return bottle.static_file(filename, root='./views')
bottle.SimpleTemplate.defaults["include_file"] = include_file"""


repo = Repo()
auth = AuthService(repo)

# Helper metode

def izracunaj_hash_gesla(geslo):
    m = hashlib.sha256()
    m.update(geslo.encode("utf-8"))
    return m.hexdigest()

def preberi_in_izbrisi_cookie(cookie, default):
    """Preberi vrednost cookie-ja in ga izbriši"""
    vrednost = request.get_cookie(cookie, default, secret=SECRET_COOKIE_KEY)
    response.delete_cookie(cookie, path="/")
    return vrednost

# TODO: Dodaj tabelo uporabnik v podatkovno bazo
def preveriUporabnika(): 
    id_uporabnika = request.get_cookie("id", secret=SECRET_COOKIE_KEY)
    if id_uporabnika:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try: 
            cur.execute("SELECT id_uporabnika FROM uporabnik WHERE id_uporabnika = %s", [id_uporabnika])
            id_uporabnika = cur.fetchone()[0]
        except:
            id_uporabnika = None
        if id_uporabnika: 
            return id_uporabnika
    redirect(url('prijava_get'))

def nastavi_cookie(cookie, vrednost=""):
    """Nastavi vrednost cookie-ja"""
    response.set_cookie(cookie, vrednost, path="/", secret=SECRET_COOKIE_KEY)

def nastavi_sporocilo(sporocilo=None):
    staro = request.get_cookie("sporocilo", secret=SECRET_COOKIE_KEY)
    if sporocilo is None:
        response.delete_cookie("sporocilo", path="/")
    else:
        response.set_cookie("sporocilo", sporocilo, secret=SECRET_COOKIE_KEY, path="/")

# za ločitev med prijavo in odjavo
def preveriZnacko():
    if request.get_cookie("id", secret = SECRET_COOKIE_KEY):
        return 1
    else:
        return 0

@get("/views/images/<filepath:re:.*\.(jpg|png|gif|ico|svg)>")
def img(filepath):
    return static_file(filepath, root="views/images")

@route("/static/<filename:path>", name="static")
def static(filename):
    return static_file(filename, root=static_dir)

"""def cookie_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print("KLIČEM COOKIE_REQUIRED")
        vloga = request.get_cookie("vloga")
        ime = request.get_cookie("ime")
        priimek = request.get_cookie("priimek")
        email = request.get_cookie("email")
        geslo1 = request.get_cookie("geslo")
        geslo2 = request.get_cookie("geslo2")


                # emaila tu ne pregledujem, saj ni potreben za prijavo

        if vloga: # and ime and priimek and geslo1 and geslo2:
            return f(*args, **kwargs)
        return template("registracija.html", url=url, napaka="Za ogled vizualizacij si moraš izbrati vlogo!", vloga=vloga)
    return decorated"""


# zacetna stran
@get('/', name='index')
def index():
    znacka = preveriZnacko()
    return template('zacetna_stran1.html', url=url, znacka=znacka)

@get('/registracija', name='registracija_get')
def registracija_get():
    napaka = nastavi_sporocilo()  # Ker je argument None, bo cookie 'sporocilo' izbrisan
    vloga = request.get_cookie("vloga")
    ime = request.get_cookie("ime")
    priimek = request.get_cookie("priimek")
    email = request.get_cookie("email", "_")
    navijaska_drzava = request.get_cookie("navijaska_drzava")
    return template("registracija1.html", url=url, napaka=None, vloga=None, ime=ime, priimek=priimek, navijaska_drzava=navijaska_drzava, email=email)


@post('/registracija', name='registracija_post')
def registracija_post():
    vloga = request.forms.vloga # type: ignore
    ime = request.forms.ime # type: ignore
    priimek = request.forms.priimek # type: ignore
    email = request.forms.email # type: ignore
    geslo = request.forms.geslo # type: ignore
    geslo2 = request.forms.geslo2 # type: ignore
    navijaska_drzava = request.forms.navijaska_drzava # type: ignore

    try: 
        cur.execute(f"SELECT * FROM uporabnik WHERE email = {email}")
        data = cur.fetchall()
        if data != []:
            email = None
    except:
        email = email
    
    # print("PRIŠEL DO SEM")

    
    while True:
        if email is None:
            nastavi_sporocilo('Registracija ni možna ta email je že v uporabi!')
        elif len(geslo) < 4:
            nastavi_sporocilo('Geslo mora imeti vsaj 4 znake!')
        elif geslo != geslo2:
            nastavi_sporocilo('Gesli se ne ujemata!')
        else: # ni napake, skočimo iz zanke
            break
        # imamo napako, nastavimo piškotke in preusmerimo
        nastavi_cookie('ime', ime)
        nastavi_cookie('priimek', priimek)
        nastavi_cookie('vloga', vloga)
        nastavi_cookie('navijaska_drzava', navijaska_drzava)
        nastavi_cookie('email', str(email))
        
        redirect(url('registracija_get'))
    
    hash_gesla = izracunaj_hash_gesla(geslo)
    print("Hash gesla:", hash_gesla)

    try:
        print("Vnos v bazo...")
        cur.execute("""
            INSERT INTO uporabniki (ime, priimek, email, geslo, navijaska_drzava)
            VALUES ('a', 'a', 'a', 'a', 'a');
        """, (ime, priimek, email, hash_gesla, navijaska_drzava))
        
        id_uporabnika = cur.fetchone()[0]
        conn.commit()
        print("Vnos uspešen!")
        nastavi_cookie('id', id_uporabnika)
    except:
        nastavi_sporocilo('Napaka pri vnosu v bazo!')
    
    redirect(url('registracija_get'))
    return
    


@get('/about', name='about')
def about():
    znacka = preveriZnacko()
    return template("about.html", naslov='O podjetju', znacka=znacka, url=url)


@get('/odjava', name='odjava')
def odjava():
    response.delete_cookie("id")
    redirect(url('index'))



if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)
