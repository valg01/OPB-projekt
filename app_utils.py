import hashlib


class DBUtils:
    @staticmethod
    def dobi_prvi_rezultat(cur):
        return cur.fetchone()[0]

    @staticmethod
    def izracunaj_hash_gesla(geslo):
        return hashlib.sha256(geslo.encode()).hexdigest()


class RegistracijaUtils:
    @staticmethod
    def _email_ze_obstaja_q(email, cur):
        try:
            cur.execute(f"SELECT * FROM uporabnik WHERE email = {email}")
            data = cur.fetchall()
            if data != []:
                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _gesli_enaki(geslo, ponovljeno_geslo):
        return geslo == ponovljeno_geslo

    @staticmethod
    def _geslo_prekratko(geslo):
        return len(geslo) < 4

    @staticmethod
    def registracija_ok_q(geslo, ponovljeno_geslo, email, cur):
        """Pogleda, če je registracija ok. Če je, vrne (True, ""), sicer pa (False, {{napaka}})."""
        if RegistracijaUtils()._email_ze_obstaja_q(email, cur):
            return (False, "Registracija ni možna ta email je že v uporabi!")
        elif RegistracijaUtils()._geslo_prekratko(geslo):
            return (False, "Geslo mora imeti vsaj 4 znake!")
        elif not RegistracijaUtils()._gesli_enaki(geslo, ponovljeno_geslo):
            return (False, "Gesli se ne ujemata!")
        else:
            return (True, "")


class GeneralUtils:
    @staticmethod
    def flatten_list(l):
        return [item for sublist in l for item in sublist]
