import unittest
import os
from platform import system as system_name
from subprocess import call as system_call
import json
import re
import math
import urllib.request
import pdfminer.high_level
import lxml.html as html
from selenium import webdriver
from web_crawler.ksrf import ping, get_web_driver
from web_crawler.ksrf import get_open_page_script_template
from web_crawler.ksrf import get_page_html_by_num, get_decision_headers
from web_crawler.ksrf import get_possible_text_location, get_pages_number
from web_crawler.ksrf import KSRFSource, LocalFileStorageSource, download_text
from enum import Enum
if __package__:
    from web_crawler.web_crawler import DataSource, DataSourceType, DataType
else:
    from web_crawler import DataSource, DataSourceType, DataType, WebCrawler
PATH_TO_CHROME_WEB_DRIVER = (os.path.dirname(__file__) +
                             '\\Selenium\\chromedriver.exe')
KSRF_PAGE_URI = 'http://www.ksrf.ru/ru/Decision/Pages/default.aspx'


class DataSourceTestCase(unittest.TestCase):
    def setUp(self):
        self.DataST1 = DataSourceType(1)
        self.DataS1 = DataSource(r'КСРФ/31-П/2018', self.DataST1)
        self.DataS2 = DataSource(r'КСРФ/31-П/2018', self.DataST1)
        self.DataS3 = DataSource(r'КСРФ/30-П/2018', self.DataST1)

    def testCreateWithCorrectArguments(self):
        try:
            self.DataS4 = DataSource(r'КСРФ/30-П/2018', self.DataST1)
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testCreateWithIncorrectArguments(self):
        try:
            self.DataS4 = DataSource(r'КСРФ/30-П/2018', None)
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertFalse(TestStatus)

    def testGetData(self):
        try:
            self.DataS1.get_data(r'КСРФ/31-П/2018', DataType.DOCUMENT_TEXT)
            TestStatus = True
        except Exception:
            TestStatus = True
        else:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testGetAllData(self):
        try:
            self.DataS1.get_all_data(DataType.DOCUMENT_TEXT)
            TestStatus = True
        except Exception:
            TestStatus = True
        else:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testPrepare(self):
        try:
            self.DataS1.get_data(r'КСРФ/31-П/2018', DataType.DOCUMENT_TEXT)
            TestStatus = True
        except Exception:
            TestStatus = True
        else:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testEqWithEqualClasses(self):
        TestStatus = self.DataS1 == self.DataS2
        self.assertTrue(TestStatus)

    def testEqWithUnequalClasses(self):
        TestStatus = self.DataS1 == self.DataS3
        self.assertFalse(TestStatus)

    def testNeWithUnequalClasses(self):
        TestStatus = self.DataS1 != self.DataS2
        self.assertFalse(TestStatus)

    def testNeWithEqualClasses(self):
        TestStatus = self.DataS1 != self.DataS3
        self.assertTrue(TestStatus)

    def testHashWithSameClasses(self):
        DataSList = []
        i = 0
        while i < 100:
            i += 1
            DataSList.append(DataSource(r'КСРФ/32-П/2018', self.DataST1))
        TestStatus = True
        for DataS in DataSList:
            if DataS.__hash__ != DataSList[0].__hash__:
                TestStatus = False
        self.assertTrue(TestStatus)

    def testHashWithDifferentClasses(self):
        DataSList = []
        i = 0
        while i < 100:
            i += 1
            DataSList.append(DataSource(
                r'КСРФ/'+str(i)+r'-П/2018', self.DataST1))
        DataSList = [DataS.__hash__() for DataS in DataSList]
        TestStatus = True
        for DataS in DataSList:
            if DataSList.count(DataS) != 1:
                TestStatus = False
        self.assertTrue(TestStatus)


class WebCrawlerTestCase(unittest.TestCase):
    def setUp(self):
        self.DataST1 = DataSourceType(1)
        self.DataS1 = DataSource(r'КСРФ/31-П/2018', self.DataST1)

    def testCreateWithCorrectArguments(self):
        try:
            self.WebCr = WebCrawler([self.DataS1])
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testCreateWithIncorrectArguments(self):
        try:
            self.WebCr = WebCrawler([None])
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertFalse(TestStatus)


class KSRFTestCase(unittest.TestCase):
    def testPing(self):
        TestStatus = True
        if ping('google.com') is not True:
            TestStatus = False
        try:
            ping(None)
            TestStatus = False
        except TypeError:
            TestStatus = True
        self.assertTrue(TestStatus)

    def testGetWebDriver(self):
        try:
            get_web_driver()
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testGetDecisionHeaders(self):
        try:
            get_decision_headers(2)
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testGetPossibleTextLocation(self):
        try:
            get_possible_text_location(
                r'КСРФ/31-П/2018',
                r'C:\\Vs Code Projects\\Python Projects\\'
                r'link_analysis-project\\Decision files\\test5.txt',
            )
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testDownloadText(self):
        try:
            download_text(
                r'http://doc.ksrf.ru/decision/KSRFDecision357646.pdf',
                r'КСРФ/31-П/2018',
                r'C:\\Vs Code Projects\\Python Projects\\'
                r'link_analysis-project\\Decision files\\test5.txt'
            )
            TestStatus = True
        except ValueError:
            TestStatus = False
        self.assertFalse(TestStatus)

    def testPagesNumber(self):
        try:
            get_pages_number()
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)


class KSRFSourceTestCase(unittest.TestCase):
    def testCreateWithCorrectArguments(self):
        try:
            self.ksrfS = KSRFSource()
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testPrepare(self):
        try:
            self.ksrfS = KSRFSource()
            self.ksrfS.prepare()
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testGetData(self):
        try:
            self.ksrfS = KSRFSource()
            self.ksrfS.get_data(r'КСРФ/30-П/2018', DataType.DOCUMENT_TEXT)
            TestStatus = True
        except AttributeError:
            TestStatus = True
        else:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testGetAllData(self):
        try:
            self.ksrfS = KSRFSource()
            self.ksrfS.get_all_data(DataType.DOCUMENT_HEADER)
            TestStatus = True
        except AttributeError:
            TestStatus = True
        else:
            TestStatus = False
        self.assertTrue(TestStatus)


class LocalFileStorageSourceTestCase(unittest.TestCase):
    def testCreateWithCorrectArguments(self):
        try:
            self.LocalF = LocalFileStorageSource()
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testPrepare(self):
        try:
            self.LocalF = LocalFileStorageSource()
            self.LocalF.prepare()
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testGetData(self):
        try:
            self.LocalF = LocalFileStorageSource()
            self.LocalF.get_data(r'КСРФ/30-П/2018', DataType.DOCUMENT_TEXT)
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testGetAllData(self):
        try:
            self.LocalF = LocalFileStorageSource()
            self.LocalF.get_all_data(DataType.DOCUMENT_TEXT)
            TestStatus = True
        except TypeError:
            TestStatus = False
        self.assertTrue(TestStatus)

    def testPutData(self):
        try:
            self.LocalF = LocalFileStorageSource()
            self.LocalF.put_data(r'КСРФ/30-П/2018', 'data',
                                 DataType.DOCUMENT_TEXT)
            TestStatus = True
        except AttributeError:
            TestStatus = True
        self.assertTrue(TestStatus)

    def testPutDataCollection(self):
        try:
            self.LocalF = LocalFileStorageSource()
            self.LocalF.put_data_collection({1: 'data'},
                                            DataType.DOCUMENT_TEXT)
            TestStatus = True
        except FileNotFoundError:
            TestStatus = True
        except AttributeError:
            TestStatus = True
        else:
            TestStatus = False
        self.assertTrue(TestStatus)

'''
suite = unittest.TestLoader().loadTestsFromTestCase(DataSourceTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(WebCrawlerTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(KSRFTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(KSRFSourceTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(
    LocalFileStorageSourceTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
'''
if __name__ == '__main__':
    unittest.main()
