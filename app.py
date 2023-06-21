#!/usr/bin/python
# -*- encoding: utf-8 -*-

import bottle
from bottle import get, post, run, request, template, redirect, response, url
from Data.Database import Repo
from Data.Modeli import *
from Data.Services import AuthService
from functools import wraps
import os

SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)


def include_file(filename):
    return bottle.static_file(filename, root='./views')

bottle.SimpleTemplate.defaults["include_file"] = include_file


repo = Repo()
auth = AuthService(repo)

def pridobi_osnovne_podatke():
    """Vrne osnovne podatke v obliki tuppla:
    (ime, priimek, email, rojstna_drzava, vloga)
    """

def cookie_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print("KLIČEM COOKIE_REQUIRED")
        vloga = request.get_cookie("vloga")
        ime = request.get_cookie("ime")
        priimek = request.get_cookie("priimek")
        email = request.get_cookie("email")
        geslo1 = request.get_cookie("geslo")
        geslo2 = request.get_cookie("geslo2")
        # if geslo1 != geslo2:
        #    return template("registracija.html", url=url, napaka="Zapisani gesli morata biti enaki!", vloga=vloga)
        rojstna_drzava = request.get_cookie("rojstna-drzava")
        # emaila tu ne pregledujem, saj ni potreben za prijavo

        """ if vloga and ime and priimek and geslo1 and geslo2 and rojstna_drzava:
            return f(*args, **kwargs) """
        return template("registracija.html", url=url, napaka="Za ogled vizualizacij si moraš izbrati vlogo!", vloga=vloga)
    return decorated

@get('/')
@cookie_required
def index():
    vloga = request.get_cookie("vloga")
    return template('predstavitev_vizualizacij.html', url=url, vloga=vloga)

@get('/registracija')
def registracija_get():
    return template("registracija.html", url=url, napaka=None, vloga=None)


@post('/registracija', name='registracija')
def registracija():
    """
    Prijavi uporabnika v aplikacijo. Vsak uporabnik si lahko izbere eno izmed sledečih vlog: novinec, entuziast, eskpert.
    Če je registracija vloge uspešna, ustvari piškotke o uporabniku in njegovi roli.
    Drugače sporoči, da je registracija vloge neuspešna.
    """
    vloga = request.forms.get('vloga')
    ime = request.forms.get('ime')
    priimek = request.forms.get('priimek')
    email = request.forms.get('email')
    geslo1 = request.forms.get('geslo')
    geslo2 = request.forms.get('geslo_ponovno')
    rojstna_drzava = request.forms.get('rojstna_drzava')
    trenutna_drzava = request.forms.get('trenutna_drzava')
    
    if geslo1 != geslo2:
        return template("registracija.html", url=url, napaka="Zapisani gesli morata biti enaki!", vloga=vloga)

    # TODO: Zapisi uporabnika v bazo
    print('username: ', vloga)
    if not auth.obstaja_vloga(vloga):
        return template("registracija.html", napaka="Vloga s tem imenom ne obstaja", url=url, vloga=vloga)

    response.set_cookie("vloga", vloga)
    response.set_cookie("ime", ime)
    response.set_cookie("priimek", priimek)
    response.set_cookie("email", email)
    response.set_cookie("geslo", geslo1)
    response.set_cookie("rojstna_drzava", rojstna_drzava)
    response.set_cookie("trenutna_drzava", trenutna_drzava)

    redirect(url('/'))


@get('/odjava', name='odjava')
def odjava():
    """
    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku in njegovi vlogi.
    """
    response.delete_cookie("vloga")
    return template('registracija.html', napaka=None, url=url, vloga=None)


if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)
