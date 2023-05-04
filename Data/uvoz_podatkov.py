import pandas as pd
import numpy as np
from utils import TABLE_DATA
import auth_public as auth
import requests
import io
import warnings
import Database


DEFAULT_DATE = '1900-01-01'
USE_CAMEL_CASE = False
# Če želite tabele odstraniti ter jih napolniti še enkrat, je trenutno treba tabele "na roko" izbrisati ter nastaviti vrednost PONOVNO_ZAPISI_TABELE na True
PONOVNO_ZAPISI_TABELE = True  # Ne bo ničesar naredilo, če so tabele že ustvarjenje. Znotraj Database.py tabela namreč ustvari preko ukaza "CREATE TABLE IF NOT EXISTS ..."
PONOVNO_NAPOLNI_TABELE = True  # PAZI: Napolnjevanje tabel ni idempotetna operacija: Če tabelo napolnemo dvakrat, se bodo v naši podatkovni bazi podvojili podatki


# Enable the warning filter
warnings.filterwarnings('always')


def ustvari_url(ime_tabele):
    return f"https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/{ime_tabele}.csv"


def shrani_df(ime_tabele, column_types_mapping):
    seznam_imen_stolpcev = column_types_mapping.keys()
    # Preberi podatke iz Githuba
    s = requests.get(ustvari_url(ime_tabele)).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')), usecols=seznam_imen_stolpcev) 
    # Nastavitev pravih tipov pandasovih stolpcev
    for ime_stolpca in seznam_imen_stolpcev:
        if column_types_mapping[ime_stolpca] == "date":
            # Nekateri datumi so shranjeni kot NaN, NaT ali "not available". Te nadomestim z default vrednostjo DEFAULT_DATE
            df[ime_stolpca] = df[ime_stolpca].replace("not available", DEFAULT_DATE)
            df[ime_stolpca].fillna(DEFAULT_DATE, inplace=True)
            # not availble zamenjava s tem datumom, ker imava problem v loadu, v SQL bova dala NAN
            df[ime_stolpca] = pd.to_datetime(df[ime_stolpca], format='%Y-%m-%d')
        else:
            df[ime_stolpca] = df[ime_stolpca].astype(column_types_mapping[ime_stolpca])
    return df


repo = Database.Repo()


def preberi_in_ustvari(data):
    for ime_tabele, dict_columns_and_types in data.items():

        # Branje in čiščenje/formatiranje tabele
        df_trenutna = shrani_df(ime_tabele, dict_columns_and_types)

        # Ustvarjanje tabele. Bodi pozoren na to, da se znotraj Database.py tabela ustvari preko ukaza "CREATE TABLE IF NOT EXISTS ..."
        if PONOVNO_ZAPISI_TABELE:
            repo.df_to_sql_create(df_trenutna, ime_tabele, column_types_mapping=dict_columns_and_types, use_camel_case=USE_CAMEL_CASE)

        # Dodajanje novih podatkov v tabelo
        if PONOVNO_NAPOLNI_TABELE:
            repo.df_to_sql_insert(df_trenutna, ime_tabele,use_camel_case=USE_CAMEL_CASE)
    

preberi_in_ustvari(TABLE_DATA)
