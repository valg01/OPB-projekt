import pandas as pd
import utils as data
import psycopg2

conn = psycopg2.connect(
    host="baza.fmf.uni-lj.si",
    database="sem2023_valg",
    user="valg",
    password="mcw4mi0q"
)

def ustvari_url(ime_tabele):
    return f"https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/{ime_tabele}.csv"

def preberi_in_ustvari(data):
    for key, lst in data.items():
        df = pd.read_csv(ustvari_url(key), usecols=lst)
        df.to_sql(key, conn, if_exists="replace", index = False)
    conn.close()

print(preberi_in_ustvari(data.data))
