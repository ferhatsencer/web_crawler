# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import requests
import urllib3.exceptions
from bs4 import BeautifulSoup
import re
import queue
import threading
import urllib.error
import requests.exceptions
import unittest
import validators
import time
import os

from logger import Logger

response_err_urls = []
ssl_error_urls = []
connection_error_urls = []
new_con_err_urls = []
timeout_err_urls = []
max_entry_err_urls = []
invalidURL = []
_Exception = []

total_url_counter = 0


def get_response(link):
    return requests.get(link)


class Crawler(threading.Thread):

    def __init__(self, root_url, url_list, visited_urls, thread_lock, output_file, output_filename, logger):
        threading.Thread.__init__(self)
        self.output_filename = output_filename
        self.visited_urls = visited_urls
        self.thread_lock = thread_lock
        self.url_list = url_list
        self.root_url = root_url
        self.output_file = output_file
        global total_url_counter
        self.logger = logger

    def add_url(self, temp_url):
        self.url_list.put(temp_url)
        self.visited_urls.add(temp_url)
        return len(self.visited_urls)

    def write_log(self, temp_url):
        output = str(total_url_counter) + ":" + str(time.ctime()) + " --- " + str(temp_url) + "\n"
        self.output_file.write(output)
        return self.output_filename

    def get_urls(self, soup):
        global total_url_counter
        temp_url = ""
        for i in soup.findAll('a', attrs={'href': re.compile("^(http|https)://")}):
            temp_url = i.get("href")
            self.thread_lock.acquire()
            if temp_url not in self.visited_urls:
                self.add_url(temp_url)
                total_url_counter = total_url_counter + 1
                print(total_url_counter, time.ctime(), temp_url)
                self.write_log(temp_url)
            self.thread_lock.release()
        return validators.url(temp_url)

    def handle_exceptions(self, link):
        global response
        try:
            response = requests.get(link)
        except urllib.error.URLError as e:
            self.logger.log_errors(response_err_urls, "response_error_log.txt", link)
            return False
        except requests.exceptions.SSLError as e:
            self.logger.log_errors(ssl_error_urls, "ssl_error_log.txt", link)
            return False
        except (urllib3.exceptions.ConnectionError, requests.exceptions.ConnectionError) as e:
            self.logger.log_errors(connection_error_urls, "connection_error_log.txt", link)
            return False
        except urllib3.exceptions.NewConnectionError as e:
            self.logger.log_errors(new_con_err_urls, "new_connection_error_log.txt", link)
            return False
        except urllib3.exceptions.TimeoutError as e:
            self.logger.log_errors(timeout_err_urls, "timeout_error_log.txt", link)
            return False
        except urllib3.exceptions.MaxRetryError as e:
            self.logger.log_errors(max_entry_err_urls, "max_entry_error_log.txt", link)
            return False
        except requests.exceptions.InvalidURL as e:
            self.logger.log_errors(invalidURL, "invalid_url_log.txt", link)
            return False
        except Exception as e:
            self.logger.log_errors(_Exception, "_Exception.txt", link)
            return False

        return True

    def run(self):
        global response
        while True:
            link = self.url_list.get()
            response = self.logger.store_exceptions_to_db(link, response_err_urls,
                                                      ssl_error_urls,
                                                      connection_error_urls,
                                                      new_con_err_urls,
                                                      timeout_err_urls,
                                                      max_entry_err_urls,
                                                      invalidURL,
                                                      _Exception)
            if not response:
                continue
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                self.get_urls(soup=soup)

    def __del__(self):
        self.output_file.close()


class Test1(unittest.TestCase):
    global total_url_counter
    thread_lock = threading.Lock()
    threads = []

    visited_urls = set()
    visited_urls.add("https://www.google.com")
    url_list = queue.Queue()

    root_url = "https://www.google.com"
    url_list.put(root_url)
    output_filename = ".unit_test_output.txt"

    c = Crawler(root_url=root_url, url_list=url_list, visited_urls=visited_urls,
                thread_lock=thread_lock, output_file=open(output_filename, "w"), output_filename=output_filename, logger=Logger(thread_lock, total_url_counter))

    def test_add_url(self):
        self.assertEqual(self.c.add_url("https://www.google.com"), len(self.visited_urls))

    def test_write_log(self):
        self.assertEqual(os.path.isfile(self.c.write_log("https://www.google.com")), True)

    def test_get_urls(self):
        self.assertTrue(self.c.get_urls(soup=BeautifulSoup(requests.get("https://www.google.com").text, "html.parser")),
                        True)

    def test_get_response(self):
        self.assertTrue(get_response("https://www.google.com").text.__contains__("http"), True)

    def test_error_log(self):
        self.assertTrue(self.c.logger.log_errors(response_err_urls, ".unit_test_err.txt", "https://www.google.com"),
                        True)


if __name__ == '__main__':

    thread_lock = threading.Lock()
    threads = []

    visited_urls = set()
    url_list = queue.Queue()

    root_url = "https://www.reddit.com/"
    url_list.put(root_url)
    output_filename = "output.txt"
    output_file = open(output_filename, "w")
    thread_num = 8

    # unittest.main()

    for i in range(thread_num):
        t = Crawler(root_url=root_url, url_list=url_list, visited_urls=visited_urls,
                    thread_lock=thread_lock, output_file=output_file, output_filename=output_filename, logger=Logger(thread_lock, total_url_counter))
        t.start()
        threads.append(t)

    print(len(threads), thread_num)

    for t in threads:
        t.join()
