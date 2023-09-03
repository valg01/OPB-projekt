# uvozimo psycopg2
import psycopg2
import psycopg2.extensions
import psycopg2.extras
import os

psycopg2.extensions.register_type(
    psycopg2.extensions.UNICODE
)  # se znebimo problemov s šumniki

import warnings
from datetime import date
from re import sub
from typing import Callable, List, Type, TypeVar

from pandas import DataFrame

import Data.auth_public as auth
from Data.Modeli import Uporabnik

# import dataclasses
# Ustvarimo generično TypeVar spremenljivko. Dovolimo le naše entitene, ki jih imamo tudi v bazi
# kot njene vrednosti. Ko dodamo novo entiteno, jo moramo dodati tudi v to spremenljivko.

T = TypeVar("T", Uporabnik, DataFrame)


class Repo:
    def __init__(self):
        self.conn = psycopg2.connect(
            database=auth.db,
            host=auth.host,
            user=auth.user,
            password=auth.password,
            port=os.environ.get('POSTGRES_PORT', 5432),
        )
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def dobi_gen(self, typ: Type[T], take=10, skip=0) -> List[T]:
        # Generična metoda, ki za podan vhodni dataclass vrne seznam teh objektov iz baze. Predpostavljamo, da je tabeli ime natanko tako kot je ime posameznemu dataclassu.

        # ustvarimo sql select stavek, kjer je ime tabele typ.__name__ oz. ime razreda
        tbl_name = typ.__name__
        sql_cmd = f"""SELECT * FROM {tbl_name} LIMIT {take} OFFSET {skip};"""
        self.cur.execute(sql_cmd)
        return [typ.from_dict(d) for d in self.cur.fetchall()]

    def dobi_gen_id(self, typ: Type[T], id: int, id_col="id") -> T:
        # Generična metoda, ki vrne dataclass objekt pridobljen iz baze na podlagi njegovega idja.
        tbl_name = typ.__name__
        sql_cmd = f"SELECT * FROM {tbl_name} WHERE {id_col} = %s"
        self.cur.execute(sql_cmd, (id,))

        d = self.cur.fetchone()

        if d is None:
            raise Exception(f"Vrstica z id-jem {id} ne obstaja v {tbl_name}")

        return typ.from_dict(d)

    """
    def dodaj_gen(self, typ: T, serial_col="id", auto_commit=True):
        # Generična metoda, ki v bazo doda entiteto/objekt. V kolikor imamo definiram serial stolpec, objektu to vrednost tudi nastavimo.

        tbl_name = type(typ).__name__

        cols =[c.name for c in dataclasses.fields(typ) if c.name != serial_col]
        
        sql_cmd = f'''
        INSERT INTO {tbl_name} ({", ".join(cols)})
        VALUES
        ({self.cur.mogrify(",".join(['%s']*len(cols)), [getattr(typ, c) for c in cols]).decode('utf-8')})
        '''

        if serial_col != None:
            sql_cmd += f'RETURNING {serial_col}'

        self.cur.execute(sql_cmd)

        if serial_col != None:
            serial_val = self.cur.fetchone()[0]

            # Nastavimo vrednost serial stolpca
            setattr(typ, serial_col, serial_val)

        if auto_commit: self.conn.commit()

        # Dobro se je zavedati, da tukaj sam dataclass dejansko
        # "mutiramo" in ne ustvarimo nove reference. Return tukaj ni niti potreben.
    """

    """
    def dodaj_gen_list(self, typs: List[T], serial_col="id"):
        # Generična metoda, ki v bazo zapiše seznam objekton/entitet. Uporabi funkcijo dodaj_gen, le da ustvari samo en commit na koncu.

        if len(typs) == 0: return # nič za narest

        # drugače dobimo tip iz prve vrstice
        typ = typs[0]

        tbl_name = type(typ).__name__

        cols =[c.name for c in dataclasses.fields(typ) if c.name != serial_col]
        sql_cmd = f'''
            INSERT INTO {tbl_name} ({", ".join(cols)})
            VALUES
            {','.join(
                self.cur.mogrify(f'({",".join(["%s"]*len(cols))})', i.to_dict()).decode('utf-8')
                for i in typs
                )}
        '''

        if serial_col != None:
            sql_cmd += f' RETURNING {serial_col};'

        self.cur.execute(sql_cmd)

        if serial_col != None:
            res = self.cur.fetchall()

            for i, d in enumerate(res):
                setattr(typs[i], serial_col, d[0])

        self.conn.commit()
    """

    """
    def posodobi_gen(self, typ: T, id_col = "id", auto_commit=True):
        # Generična metoda, ki posodobi objekt v bazi. Predpostavljamo, da je ime pripadajoče tabele enako imenu objekta, ter da so atributi objekta direktno vezani na ime stolpcev v tabeli.

        tbl_name = type(typ).__name__
        
        id = getattr(typ, id_col)
        # dobimo vse atribute objekta razen id stolpca
        fields = [c.name for c in dataclasses.fields(typ) if c.name != id_col]

        sql_cmd = f'UPDATE {tbl_name} SET \n ' + \
                    ", \n".join([f'{field} = %s' for field in fields]) +\
                    f'WHERE {id_col} = %s'
        
        # iz objekta naredimo slovar (deluje samo za dataclasses_json)
        d = typ.to_dict()

        # sestavimo seznam parametrov, ki jih potem vsatvimo v sql ukaz
        parameters = [d[field] for field in fields]
        parameters.append(id)

        # izvedemo sql
        self.cur.execute(sql_cmd, parameters)
        if auto_commit: self.conn.commit()
    """

    """
    def posodobi_list_gen(self, typs : List[T], id_col = "id"):
        # Generična metoda, ki  posodobi seznam entitet(objektov). Uporabimo isti princip kot pri posodobi_gen funkciji, le da spremembe commitamo samo enkrat na koncu.
        
        # Posodobimo vsak element seznama, pri čemer sprememb ne comitamo takoj na bazi
        for typ in typs:
            self.posodobi_gen(typ, id_col=id_col, auto_commit=False)

        # Na koncu commitamo vse skupaj
        self.conn.commit()
    """

    def camel_case(self, s):
        """
        Pomožna funkcija, ki podan niz spremeni v camel case zapis.
        """

        s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
        return "".join(s)

    def col_to_sql(
        self, col: str, column_types_mapping: str, use_camel_case=True, is_key=False
    ):
        """
        Funkcija ustvari del sql stavka za create table na podlagi njegovega imena
        in (python) tipa. Dodatno ga lahko opremimo še z primary key omejitvijo
        ali s serial lastnostjo. Z dodatnimi parametri, bi lahko dodali še dodatne lastnosti.
        """

        # ali stolpce pretvorimo v camel case zapis?
        if use_camel_case:
            col = self.camel_case(col)

        match column_types_mapping[col]:
            case "int":
                return f'"{col}" BIGINT{" PRIMARY KEY" if  is_key else ""}'
            case "float":
                return f'"{col}" FLOAT'
            case "bool":
                return f'"{col}" BOOL'
            case "date":
                return f'"{col}" DATE'
            case "str":
                return f'"{col}" TEXT{" PRIMARY KEY" if  is_key else ""}'

        warnings.warn(
            f"stolpec {col} se ne ujema z nobenim izmed tipov [int, float, bool, date, string]. Shranjujem ta stolpec kot tip TEXT."
        )

        return f'"{col}" TEXT{" PRIMARY KEY" if  is_key else ""}'

    def df_to_sql_create(
        self,
        df: DataFrame,
        name: str,
        column_types_mapping: str,
        add_serial=False,
        use_camel_case=True,
    ) -> str:
        """
        Funkcija ustvari in izvede sql stavek za create table na podlagi podanega pandas DataFrame-a.
        df: DataFrame za katerega zgradimo sql stavek
        name: ime nastale tabele v bazi
        add_serial: opcijski parameter, ki nam pove ali želimo dodat serial primary key stolpec
        """

        # dobimo slovar stolpcev in njihovih tipov
        cols = dict(df.dtypes)

        cols_sql = ""

        # dodamo serial primary key
        if add_serial:
            cols_sql += "Id SERIAL PRIMARY KEY,\n"

        # dodamo ostale stolpce
        # tukaj bi stolpce lahko še dodatno filtrirali, preimenovali, itd.
        cols_sql += ",\n".join(
            [
                self.col_to_sql(
                    col, column_types_mapping, use_camel_case=use_camel_case
                )
                for col, typ in cols.items()
            ]
        )

        # zgradimo končen sql stavek
        sql = f"""CREATE TABLE IF NOT EXISTS {name}(
            {cols_sql}
        )"""

        self.cur.execute(sql)
        self.conn.commit()

    def df_to_sql_insert(self, df: DataFrame, name: str, use_camel_case=True):
        """
        Vnese DataFrame v postgresql bazo. Paziti je treba pri velikosti dataframa,
        saj je sql stavek omejen glede na dolžino. Če je dataframe prevelik, ga je potrebno naložit
        po delih (recimo po 100 vrstic naenkrat), ali pa uporabit bulk_insert.
        df: DataFrame, ki ga želimo prenesti v bazo
        name: Ime tabele kamor želimo shranit podatke
        use_camel_case: ali pretovrimo stolpce v camel case zapis
        """

        cols = list(df.columns)

        # po potrebi pretvorimo imena stolpcev
        if use_camel_case:
            cols = [self.camel_case(c) for c in cols]

        # ustvarimo sql stavek, ki vnese več vrstic naenkrat
        sql_cmd = f"""INSERT INTO {name} ({", ".join([f'"{c}"' for c in cols])})
            VALUES 
            {','.join(
                self.cur.mogrify(f'({",".join(["%s"]*len(cols))})', i).decode('utf-8')
                for i in df.itertuples(index=False)
                )}
        """

        # izvedemo ukaz
        self.cur.execute(sql_cmd)
        self.conn.commit()
