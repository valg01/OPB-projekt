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


repo = Repo()
auth = AuthService(repo)

def cookie_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        cookie = request.get_cookie("vloga")
        print('cookie: ', cookie)
        if cookie:
            return f(*args, **kwargs)
        return template("vloga.html", url=url, napaka="Za ogled vizualizacij si moraš izbrati vlogo!", vloga=cookie)
    return decorated

@get('/')
@cookie_required
def index():
    vloga = request.get_cookie("vloga")
    return template('predstavitev_vizualizacij.html', url=url, vloga=vloga)

@get('/vloga')
def prijava_get():
    return template("vloga.html", url=url, napaka=None, vloga=None)


@post('/vloga', name='vloga')
def prijava():
    """
    Prijavi uporabnika v aplikacijo. Vsak uporabnik si lahko izbere eno izmed sledečih vlog: novinec, entuziast, eskpert.
    Če je prijava vloge uspešna, ustvari piškotke o uporabniku in njegovi roli.
    Drugače sporoči, da je prijava vloge neuspešna.
    """
    vloga = request.forms.get('vloga')

    print('username: ', vloga)
    if not auth.obstaja_vloga(vloga):
        return template("vloga.html", napaka="Vloga s tem imenom ne obstaja", url=url)

    response.set_cookie("vloga", vloga)
    redirect(url('/'))


@get('/odjava', name='odjava')
def odjava():
    """
    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku in njegovi vlogi.
    """
    response.delete_cookie("vloga")
    return template('vloga.html', napaka=None, url=url, vloga=None)


if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)
