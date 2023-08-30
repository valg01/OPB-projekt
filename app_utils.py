import hashlib
from psycopg2 import Error


class DBUtils:
    """
    A utility class for working with a PostgreSQL database.

    This class provides methods for connecting to a PostgreSQL database, executing SQL queries, and handling errors.

    Attributes:
        conn (psycopg2.extensions.connection): A connection to a PostgreSQL database.
    """

    @staticmethod
    def dobi_prvi_rezultat(cur):
        """
        Executes a SQL query and returns the first result.

        Args:
            cur (psycopg2.extensions.cursor): A cursor object for executing SQL queries.

        Returns:
            The first result of the executed SQL query.
        """
        return cur.fetchone()[0]

    @staticmethod
    def izracunaj_hash_gesla(geslo):
        """
        Calculates the SHA-256 hash of a given password.

        Args:
            geslo (str): The password to be hashed.

        Returns:
            str: The SHA-256 hash of the given password.
        """
        return hashlib.sha256(geslo.encode()).hexdigest()


class RegistracijaUtils:
    """
    A utility class for handling user registration.

    This class provides methods for checking if a user's registration information is valid.

    Attributes:
        None
    """

    @staticmethod
    def _email_ze_obstaja_q(email, cur):
        """
        Checks if a given email already exists in the database.

        Args:
            email (str): The email to check.
            cur (psycopg2.extensions.cursor): A cursor object for executing SQL queries.

        Returns:
            bool: True if the email already exists in the database, False otherwise.
        """
        try:
            cur.execute("SELECT * FROM uporabniki WHERE email = %s", (email,))
            data = cur.fetchall()
            if data != []:
                return True
            else:
                return False
        except Error as e:
            print(f"An error occurred: {e}")
            return False

    @staticmethod
    def _gesli_enaki(geslo, ponovljeno_geslo):
        """
        Checks if two given passwords are equal.

        Args:
            geslo (str): The first password to compare.
            ponovljeno_geslo (str): The second password to compare.

        Returns:
            bool: True if the passwords are equal, False otherwise.
        """
        return geslo == ponovljeno_geslo

    @staticmethod
    def _geslo_prekratko(geslo):
        """
        Checks if a given password is too short.

        Args:
            geslo (str): The password to check.

        Returns:
            bool: True if the password is too short, False otherwise.
        """
        return len(geslo) < 4

    @staticmethod
    def registracija_ok_q(geslo, ponovljeno_geslo, email, cur):
        """
        Checks if user registration information is valid.

        Args:
            geslo (str): The password to check.
            ponovljeno_geslo (str): The repeated password to check.
            email (str): The email to check.
            cur (psycopg2.extensions.cursor): A cursor object for executing SQL queries.

        Returns:
            tuple: A tuple containing a boolean value indicating if the registration information is valid and a string message.
                If the registration information is valid, the boolean value is True and the message is an empty string.
                If the registration information is invalid, the boolean value is False and the message is an error message.
        """
        if RegistracijaUtils()._email_ze_obstaja_q(email, cur):
            return (False, "Registracija ni mozna - ta email je ze v uporabi!")
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
