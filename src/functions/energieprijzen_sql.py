import os
# import re
import sys
import sqlite3
from time import time;
# from dateutil import parser, tz
from sqlite3 import Error

import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class EnergiePrijzen_SQL():
    def __init__(self, dbname:str = None) -> None:
        if dbname is None:
            raise Exception("No dbname in EnergiePrijzen")

        self.dbname = dbname
        self.conn = None
        pass

    def connection(self)->None:
        """ create a database connection to a SQLite database """
        try:
            if self.dbname is None:
                raise Exception("No database file name!")

            self.conn = sqlite3.connect(self.dbname)
            self.conn.row_factory = sqlite3.Row
            if PY_ENV != 'prod':
                self.conn.set_trace_callback(print)

            if not self.conn:
                raise Exception("No connection!!")
        except Error as e:
            log.error(e)
            sys.exit()

    def close(self)->None:
        try:
            self.conn.close()
        except Error as e:
            log.error(e)
            pass

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def no_table(self, table:str = None)->bool:
        try:
            sql = ""
            if table == 'user':
                sql = """ CREATE TABLE IF NOT EXISTS users (
                            user_id           INTEGER     PRIMARY KEY,
                            datetime          INTEGER,
                            ochtend           INTEGER,
                            opslag            DOUBLE,
                            melding_lager_dan DECIMAL DEFAULT (0.001),
                            melding_hoger_dan DECIMAL
                                        ); """

            if table == "energy":
                sql = """ CREATE TABLE IF NOT EXISTS energy(
                        fromdate VARCHAR(10) NOT NULL,
                        fromtime VARCHAR(5) NOT NULL,
                        kind VARCHAR(10) NOT NULL,
                        price DOUBLE NOT NULL,
                        PRIMARY KEY(fromdate,fromtime,kind)
                        ); """
            if sql != "":
                self.create_table(create_table_sql=sql)
                return True
            else:
                raise Exception("There is no SQL to run!!")
        except Exception as e:
            log.error(e)
            return False

    def create_table(self, create_table_sql:str=None)->None:
        try:
            if not create_table_sql:
                raise Exception('No create table SQL')

            self.connection()
            cur = self.conn.cursor()
            cur.execute(create_table_sql)
            self.conn.commit()
            return True
        except Exception as e:
            log.error(f'Cannot create table: {e}, {create_table_sql}')
            sys.exit(f'Cannot create table: {e}, {create_table_sql}')

    def add_price(self, **kwargs)->bool:
        try:
            short_tuple = (kwargs['fromdate'], kwargs['fromtime'], kwargs['kind'], kwargs['price'])
            self.connection()
            sql = """ INSERT OR IGNORE INTO energy (fromdate,fromtime,kind,price)
                    VALUES(?,?,?,?) """
            cur = self.conn.cursor()
            cur.execute(sql, short_tuple)
            self.conn.commit()
            return 1
        except KeyError as e:
            log.error(e)
            return -1
        except sqlite3.OperationalError as e:
            if e.args[0].startswith('no such table'):
                self.no_table(table='energy')
            else:
                log.error(e)
        except sqlite3.IntegrityError as err:
            log.error(e)
            return 0
        except Error as e:
            log.error(e)
            return -1

    def get_prices(self, date:str = None, kind:str = None)->dict:
        try:
            self.connection()
            cur = self.conn.cursor()
            if date is None:
                raise Exception('Er is geen datum om prijzen op te halen!')

            if kind is not None:
                SQL = f"""SELECT fromdate, fromtime, price, kind
                      FROM energy
                      WHERE fromdate = ? AND kind = ?"""
                output_obj = cur.execute(SQL, (date, kind, ))
            else:
                SQL =  f"""SELECT fromdate, fromtime, price, kind
                        FROM energy
                        WHERE fromdate = ?;"""
                output_obj = cur.execute(SQL, (date, ))

            results = output_obj.fetchall()
            rs_as_list = []
            for row in results:
                rs_as_list.append( {output_obj.description[i][0]:row[i] for i in range(len(row))} )

            return rs_as_list

        except sqlite3.IntegrityError:
            return 0
        except Exception as e:
            log.error(e)
            return -1

    def get_high_prices(self, date:str = None, kind:str = 'e')->dict:
        try:
            self.connection()
            cur = self.conn.cursor()

            SQL =  f"""SELECT fromdate, fromtime, price, kind
FROM energy
WHERE fromdate = ?
AND kind = ?
AND price = ( SELECT max(price) FROM energy
WHERE fromdate = ?
AND kind = ?
Group by fromdate );"""

            output_obj = cur.execute(SQL, (date, kind, date, kind, ))
            results = output_obj.fetchall()

            row_as_dict = []
            for row in results:
                row_as_dict.append( {output_obj.description[i][0]:row[i] for i in range(len(row))} )

            return row_as_dict

        except sqlite3.IntegrityError:
            return 0
        except Exception as e:
            log.error(e)
            return -1

    def get_low_prices(self, date:str = None, kind:str = 'e')->dict:
        try:
            self.connection()
            cur = self.conn.cursor()

            SQL =  f"""SELECT fromdate, fromtime, price, kind
FROM energy
WHERE fromdate = ?
AND kind = ?
AND price = ( SELECT min(price) FROM energy
WHERE fromdate = ?
AND kind = ?
Group by fromdate );"""

            output_obj = cur.execute(SQL, (date, kind, date, kind, ))
            results = output_obj.fetchall()

            row_as_dict = []
            for row in results:
                row_as_dict.append( {output_obj.description[i][0]:row[i] for i in range(len(row))} )

            return row_as_dict

        except sqlite3.IntegrityError:
            return 0
        except Exception as e:
            log.error(e)
            return -1

    def add_user(self, user_id:int = None)->int:
        short_tuple = (int(user_id), int(time()))
        try:
            self.connection()
            sql = """INSERT INTO users (user_id, datetime)
                    VALUES(?,?)"""
            cur = self.conn.cursor()
            cur.execute(sql, short_tuple)
            self.conn.commit()
            return 1
        except sqlite3.OperationalError as e:
            if e.args[0].startswith('no such table'):
                self.no_table(table='user')
            else:
                log.debug(e)
        except sqlite3.IntegrityError as err:
            return 0
        except Error as e:
            log.error(e)
            return -1

    def get_ochtend_users(self, hour:int = None)->list:
        try:
            if hour is None:
                return True

            self.connection()
            cur = self.conn.cursor()
            cur.execute("SELECT user_id FROM users WHERE ochtend = ?", (hour, ))
            return [list[0] for list in cur.fetchall()]
        except sqlite3.IntegrityError as err:
            return 0
        except Error as e:
            log.error(e)
            return -1

    def update_ochtend(self, user_id:int = None, tijd:str = None)->bool:
        try:
            if user_id is None:
                return False

            if tijd is None:
                tijd = None

            if not self.get_user(user_id=user_id):
                self.add_user(user_id=user_id)

            self.connection()
            sql = """Update users
set ochtend = ?
WHERE user_id = ?"""
            cur = self.conn.cursor()
            cur.execute(sql,(tijd, user_id,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as err:
            log.error(err)
            return False
        except Error as e:
            log.error(e)
            return False

    def get_user(self, user_id:int = None)->dict:
        """Returns sqlite dict with:"""
        """user_id, datetime, kaal_opslag_allin,ochtend, opslag,"""
        """melding_lager_dan, melding_hoger_dan """
        try:
            self.connection()
            cur = self.conn.cursor()
            return cur.execute(f"SELECT * FROM users WHERE user_id=?", (int(user_id),)).fetchone()
        except Error as e:
            log.error(e)
            return False

    def remove_user(self, user_id:int = None)->bool:
        try:
            self.connection()
            cur = self.conn.cursor()
            cur.execute(f"DELETE FROM users WHERE user_id=?", (int(user_id),))
            self.conn.commit()
            return 1
        except sqlite3.IntegrityError as err:
            return 0
        except Error as e:
            log.error(e)
            return -1

    def get_users(self)->list:
        try:
            self.connection()
            cur = self.conn.cursor()
            cur.execute("SELECT user_id FROM users")
            return [list[0] for list in cur.fetchall()]
        except Error as e:
            log.error(e)
            return False


if __name__ == "__main__":
    pass
