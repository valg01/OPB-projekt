
from Data.Database import Repo
from Data.Modeli import *
from typing import Dict
from re import sub
import dataclasses
import bcrypt
from typing import Type
from datetime import date

class AuthService:

    repo : Repo
    def __init__(self, repo : Repo):
        
        self.repo = repo
    
    def obstaja_vloga(self, uporabnik: str) -> bool:
        try:
            vloga = self.repo.dobi_gen_id(Uporabnik, uporabnik, id_col="vloga")
            return True
        except:
            return False