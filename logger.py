import time
import os
import urllib.error
import requests.exceptions
import sqlite3
import urllib3
# import sqlalchemy
# import threading
import unittest
# import PySide6

err_enum = ["response_error_log", "ssl_error_log", "connection_error_log", "new_connection_error_log",
            "timeout_error_log", "max_entry_error_log", "invalid_url_log", "_Exception"]

response_err = "RESPONSE"
ssl_err = "SSL"
connection_err = "CONNECTION"
new_con_err = "NEW_CONNECTION"
timeout_err = "TIMEOUT"
max_entry_err = "MAX_ENTRY"
invalidURL_err = "INVALID"
_Exception_err = "EXCEPTION"

db_path = "errors_db.sqlite3"


def db_connect(path):
    con = sqlite3.connect(path)
    return con


dbCon = db_connect(db_path)
cur = dbCon.cursor()


def db_insert(err_type, _id, _date, _name):
    dbCon.execute(f"INSERT INTO {err_type} (ID, DATE, NAME) VALUES ({_id}, {_date}, {_name} )")


def db_insert2(err_type, _id, _date, _name):
    sql = ("INSERT INTO " + err_type + "(ID, DATE, NAME) VALUES(?,?,?)")
    dbCon.execute(sql, (_id, _date, _name))


def db_insert3(_id, _date, _name):
    sql = "INSERT INTO CONNECTION (ID, DATE, NAME) VALUES(?,?,?)"
    dbCon.execute(sql, (_id, _date, _name))


def db_insert4():
    sql = "INSERT INTO CONNECTION (ID, DATE, NAME) VALUES('-1','2021','www.123.com')"
    dbCon.execute(sql)


def insert_link(err_type, _id, _date, _name):
    sql = '''INSERT INTO CONNECTION (ID, DATE, NAME) VALUES (?, ?, ?)'''
    cur = dbCon.cursor()
    cur.execute(sql, (_id, _date, _name))
    return cur.lastrowid


def create_table(err_type):
    dbCon.execute(
        f'''CREATE TABLE IF NOT EXISTS {err_type}
             (ID INT PRIMARY KEY    NOT NULL,
             DATE           TEXT    NOT NULL,
             NAME           TEXT    NOT NULL);''')


class Logger:
    def __init__(self, thread_lock, total_url_counter, ):
        self.thread_lock = thread_lock
        self.total_url_counter = total_url_counter
        create_table(response_err)
        create_table(ssl_err)
        create_table(connection_err)
        create_table(new_con_err)
        create_table(timeout_err)
        create_table(max_entry_err)
        create_table(invalidURL_err)
        create_table(_Exception_err)

    def log_errors(self, error_urls, error_log_file, link):
        self.thread_lock.acquire()
        error_urls.append(link)
        error_log = open(error_log_file, "w+")
        error_log.write(str(self.total_url_counter) + ":" + str(time.ctime()) + " --- " + str(link) + "\n")
        error_log.close()
        self.thread_lock.release()
        return os.path.isfile(error_log_file)

    def log_errors_to_db(self, err_type, error_urls, error_log_file, link):
        self.thread_lock.acquire()
        error_urls.append(link)
        id = self.total_url_counter
        date = str(time.ctime())
        name = str(link)
        # db_insert(err_type, id, date, name)
        insert_link(err_type, id, date, name)
        self.thread_lock.release()
        return True

    def store_exceptions_to_db(self, link, response_err_urls, ssl_error_urls, connection_error_urls,
                               new_con_err_urls, timeout_err_urls, max_entry_err_urls, invalidURL, _Exception):
        try:
            response = requests.get(link)
        except urllib.error.URLError as e:
            self.logger.log_errors(response_err, response_err_urls, "response_error_log.txt", link)
            return False
        except requests.exceptions.SSLError as e:
            self.logger.log_errors(ssl_err, ssl_error_urls, "ssl_error_log.txt", link)
            return False
        except (urllib3.exceptions.ConnectionError, requests.exceptions.ConnectionError) as e:
            self.logger.log_errors(connection_err, connection_error_urls, "connection_error_log.txt", link)
            return False
        except urllib3.exceptions.NewConnectionError as e:
            self.logger.log_errors(new_con_err, new_con_err_urls, "new_connection_error_log.txt", link)
            return False
        except urllib3.exceptions.TimeoutError as e:
            self.logger.log_errors(timeout_err, timeout_err_urls, "timeout_error_log.txt", link)
            return False
        except urllib3.exceptions.MaxRetryError as e:
            self.logger.log_errors(max_entry_err, max_entry_err_urls, "max_entry_error_log.txt", link)
            return False
        except requests.exceptions.InvalidURL as e:
            self.logger.log_errors(invalidURL_err, invalidURL, "invalid_url_log.txt", link)
            return False
        except Exception as e:
            self.logger.log_errors(_Exception_err, _Exception, "_Exception.txt", link)
            return False

        return response


class Test1(unittest.TestCase):
    c = Logger
    err_type = connection_err

    _id = -1
    _date = str(time.ctime())
    _name = 'www.google.com'

    # db_path = "errors_db.sqlite3"
    #
    # dbCon = sqlite3.connect(db_path)

    create_table(connection_err)
    # dbCon.execute(f"INSERT INTO {err_type} (ID, DATE, NAME) VALUES (-1, '2021', 'www.google.com' )")

    # def test_1(self):
    #     self.assertEqual(str("www.google.com"), str(dbCon.execute("SELECT NAME FROM CONNECTION").fetchone()[0]))

    # db_insert2(err_type, _id, _date, _name)
    # db_insert3(_id, _date, _name)
    # db_insert4()
    # cur.execute("INSERT INTO CONNECTION (ID, DATE, NAME) VALUES('-1', '2021', 'www.123.com')")
    # cur.execute("INSERT INTO CONNECTION (ID, DATE, NAME) VALUES('-2', '2020', 'www.345.com')")

    def test_2(self):
        record = dbCon.execute("SELECT NAME FROM CONNECTION").fetchall()
        self.assertTrue(str('www.google.com'), str(record[0]))
        print(str(record[1]))
