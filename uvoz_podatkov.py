import pandas as pd
import numpy as np
import utils
import auth_public as auth
import psycopg2

DEFAULT_DATE = pd.Timestamp('1900-01-01')

conn = psycopg2.connect(
    host=auth.host, database=auth.db, user=auth.user, password=auth.password
)


def ustvari_url(ime_tabele):
    return f"https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv/{ime_tabele}.csv"



def preberi_in_ustvari(data):
    for key, dict_columns_and_types in data.items():
        seznam_imen_stolpcev = dict_columns_and_types.keys()
        df = pd.read_csv(ustvari_url(key), usecols=seznam_imen_stolpcev)
        # "CREATE TABLE IF NOT EXISTS "
        # df.to_sql(key, conn, if_exists="replace", index = False)
        for ime_stolpca in seznam_imen_stolpcev:
            if dict_columns_and_types[ime_stolpca] == "date":
                df[ime_stolpca] = df[ime_stolpca].replace("not available", '1900-01-01')
                # not availble zamenjava s tem datumom ker imava problem v loadu, v SQL bova dala NAN
                df[ime_stolpca] = pd.to_datetime(df[ime_stolpca], format='%Y-%m-%d')
            else:
                df[ime_stolpca] = df[ime_stolpca].astype(
                    dict_columns_and_types[ime_stolpca]
                )
    conn.close()


print(preberi_in_ustvari(utils.data))
