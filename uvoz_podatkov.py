import pandas as pd
import numpy as np
import utils
import psycopg2

DEFAULT_DATE = pd.Timestamp('1900-01-01')

conn = psycopg2.connect(
    host="baza.fmf.uni-lj.si", database="sem2023_valg", user="valg", password="mcw4mi0q"
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
                #not availble zamenjava s tem datumom ker imava problem v loadu, v SQL bova dala NAN
                df[ime_stolpca] = pd.to_datetime(df[ime_stolpca], format='%Y-%m-%d')
            else:
                df[ime_stolpca] = df[ime_stolpca].astype(
                    dict_columns_and_types[ime_stolpca]
                )
        
        # print(preberi_in_ustvari(utils.data))
        print(df.dtypes.map(utils.dtype_mapping))
        #print(df.dtypes.to_dict())


        # print(df)
        # slovar_stolpcev_in_tipov = df.dtypes.sql_type() #to_dict()
        # print(slovar_stolpcev_in_tipov)
        # create = f"CREATE TABLE IF EXISTS {key}"
        # i = 0
        # for st, tip in slovar_stolpcev_in_tipov.items():
        #     if i == 0:
        #          create.append(f"{st} {tip}")
        #     else:
        #         create.append(f", {st} {tip}")
    conn.close()



print(preberi_in_ustvari(utils.data))