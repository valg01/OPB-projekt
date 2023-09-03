import psycopg2
import os
# Skopiraj datoteko v auth.py in vnesi podatke za priklop na bazo
db = "sem2023_valg"
host = "baza.fmf.uni-lj.si"
user = "javnost"
password = "javnogeslo"



connection_port = os.environ.get('POSTGRES_PORT', 5432)

def connect():
    return psycopg2.connect(
        host=host, port=connection_port, database=db, user=user, password=password
    )

