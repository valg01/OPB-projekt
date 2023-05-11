#!/usr/bin/python
# -*- encoding: utf-8 -*-

import bottle
from bottle import get, post, run, request, template, redirect, response, url
from Data.Database import Repo
from Data.Modeli import *
from Data.Services import AuthService
from functools import wraps
import os
from bottle import TEMPLATE_PATH

SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
TEMPLATE_PATH.insert(0, 'views/')

repo = Repo()
auth = AuthService(repo)

def cookie_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        cookie = request.get_cookie("uporabnik")
        if cookie:
            return f(*args, **kwargs)
        return template("prijava.html", url=url, napaka="Potrebna je prijava!")
    return decorated

@get('/prijava')
def prijava():
    return template('prijava.html', url=url, napaka=None)


@post('/prijava')
def prijava_post():
    username = request.forms.get('username')
    password = request.forms.get('password')

    if not auth.obstaja_uporabnik(username):
        return template("prijava.html", url=url, napaka="Uporabnik s tem imenom ne obstaja")

    prijava = auth.prijavi_uporabnika(username, password)
    if prijava:
        response.set_cookie("uporabnik", username)
        response.set_cookie("rola", prijava.role)
        redirect('/')  # Redirect to your desired route after successful login
    else:
        return template("prijava.html", url=url, napaka="Neuspešna prijava. Napačno geslo ali uporabniško ime.")

@get('/odjava')
def odjava():
    response.delete_cookie("uporabnik")
    response.delete_cookie("rola")
    return template('prijava.html', url=url, napaka=None)

@get('/')
@cookie_required
def index():
    return template('index.html', url=url)  # Replace with your desired template


if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)
