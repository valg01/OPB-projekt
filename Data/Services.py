import dataclasses
from datetime import date
from re import sub
from typing import Dict, Type

import bcrypt

from Data.Database import Repo
from Data.Modeli import *


class AuthService:
    repo: Repo

    def __init__(self, repo: Repo):
        self.repo = repo

    def obstaja_vloga(self, uporabnik: str) -> bool:
        try:
            vloga = self.repo.dobi_gen_id(Uporabnik, uporabnik, id_col="vloga")
            return True
        except:
            return False
