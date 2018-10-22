# coding: utf-8
import os
from os import path
from platform import system as system_name
from subprocess import call as system_call
import json
import re
import math as m
# import libs
import urllib.request
# License: MIT License

import pdfminer.high_level
# License: MIT License; Installing: python -m pip install pdfminer.six

import lxml.html as html
# License: BSD license; Installing: python -m pip install lxml

from selenium import webdriver
# License: Apache License 2.0

if __package__:
    from web_crawler.web_crawler import DataSource, DataSourceType, DataType
else:
    from web_crawler import DataSource, DataSourceType, DataType

PATH_TO_CHROME_WEB_DRIVER = (path.dirname(__file__) +
                             '\\Selenium\\chromedriver.exe')
KSRF_PAGE_URI = 'http://www.ksrf.ru/ru/Decision/Pages/default.aspx'


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP)
    request even if the host name is valid.
    """

    # Ping command count option as function of OS
    param = '-n' if system_name().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    # Pinging
    return system_call(command) == 0


def get_web_driver(pathToChromeWebDriver=PATH_TO_CHROME_WEB_DRIVER,
                   pageUri=KSRF_PAGE_URI
                   ):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(pathToChromeWebDriver, chrome_options=options)
    driver.get(pageUri)
    return driver


def get_open_page_script_template(driver, templateKey='NUMBER'):
    page = html.document_fromstring(driver.page_source)
    template = page.find_class('UserSectionFooter ms-WPBody srch-WPBody')[0]. \
        find('td/table/tbody/tr/td/a').get('href')
    template = template.split(':')[1]
    template = template.split(',')[0] + ',\'Page$' + templateKey + '\');'
    return template


def get_open_page_script(scriptTemplate, pageNum, templateKey='NUMBER'):
    return scriptTemplate.replace(templateKey, str(pageNum))


def get_page_html_by_num(driver, openPagetScriptTemplate, pageNum):
    script = get_open_page_script(openPagetScriptTemplate, pageNum)
    driver.execute_script(script)
    return driver.page_source


typePattern = re.compile(r"(?:[А-Яа-я][-А-Яа-я]*(?=-\d)|"
                         r"[А-Яа-я][-А-Яа-я]*(?=/)|[А-Яа-я][-А-Яа-я]*(?=\.)|"
                         r"[А-Яа-я][-А-Яа-я]*(?=\d))")


def get_resolution_headers(countOfPage=1, sourcePrefix='КСРФ'):
    # TO DO: check for that page is refreshed
    courtSiteContent = {}
    driver = get_web_driver()
    template = get_open_page_script_template(driver)
    page = html.document_fromstring(driver.page_source)
    for i in range(2, countOfPage + 2):
        decisions = page.find_class('ms-alternating') + \
                page.find_class('ms-vb')
        for d in decisions:
            key = d[2].text_content().replace(' ', '').upper()
            decisionID = sourcePrefix + '/' + key
            docType = sourcePrefix + '/' + typePattern.search(key)[0]
            date = d[0].text_content()
            title = d[1].text_content()
            url = d[2].getchildren()[0].get('href')
            headerElements = {'date': date, 'type': docType,
                              'title': title, 'url': url}
            if decisionID not in courtSiteContent:
                courtSiteContent[decisionID] = headerElements
            else:
                if 'not unique' in courtSiteContent[decisionID]:
                    eggs = False
                    for header in courtSiteContent[decisionID][1]:
                        if header['url'] == url:
                            eggs = True
                            break
                    if not eggs:
                        courtSiteContent[decisionID][1].append(headerElements)
                else:
                    notUniqueHeaders = \
                        [courtSiteContent[decisionID], headerElements]
                    courtSiteContent[decisionID] = \
                        ('not unique', notUniqueHeaders)
        page = html.document_fromstring(get_page_html_by_num(
                                                        driver, template, i))
    driver.quit()
    return courtSiteContent


def get_decision_filename_by_uid(uid, foldername, ext='txt'):
    return os.path.join(foldername, uid.replace('/', '_') + '.' + ext)


def load_resolution_text(url, id, folderName, isNeedSaveTxtFile=True,
                         isNeedReturnText=False):
    logo = urllib.request.urlopen(url).read()
    pathToPDF = get_decision_filename_by_uid(id, folderName, 'pdf')
    pathToTXT = get_decision_filename_by_uid(id, folderName, 'txt')
    with open(pathToPDF, "wb") as PDFFIle:
        PDFFIle.write(logo)
    with open(pathToPDF, "rb") as PDFFIle, \
            open(pathToTXT, 'wb') as TXTFile:
        pdfminer.high_level.extract_text_to_fp(PDFFIle, TXTFile)
    with open(pathToTXT, 'rt') as TXTFile:
        text = TXTFile.read()
    if (not isNeedSaveTxtFile):
        os.remove(pathToTXT)
    os.remove(pathToPDF)
    if (isNeedReturnText):
        return pathToTXT, text
    return pathToTXT


def load_resolution_texts(courtSiteContent, folderName='Decision files'):
    # TO DO: check for downloading and converting
    if not os.path.exists(folderName):
        os.mkdir(folderName)
    for decisionID in courtSiteContent:
        if 'not unique' in courtSiteContent[decisionID]:
            continue
        pathToTXT = load_resolution_text(
                courtSiteContent[decisionID]['url'],
                decisionID, folderName)
        courtSiteContent[decisionID]['path to text file'] = pathToTXT
    return courtSiteContent


def get_page_count(page, elemOnPage=20):
    countOfElem = int(page.find_class('ms-formlabel')[0].
                    getchildren()[1].text_content().
                    split(':')[1].strip())
    return m.ceil(countOfElem / elemOnPage)


class KSRFWebSource(DataSource):
    _temp_folder = 'ksrf_temp_folder'
    _decition_urls = dict()
    PAGE_COUNT = 1571  # need fix. Pip error is intended.
    _database_source = None

    def __init__(self, dataBaseSource):
        if (not isinstance(dataBaseSource, DataSource)):
            raise TypeError('dataBaseSource should be an inheriter of\
                DataSource class')
        super().__init__('KSRFWebSource', DataSourceType.WEB_SOURCE)
        self._database_source = dataBaseSource

    def prepare(self):
        '''
        It try to prepare the data source for work and
        return False if preparing have failed.
        It return True if all is ok.
        '''
        try:
            res = ping(KSRF_PAGE_URI)
            if (not res):
                return False
            headers = self._database_source.get_all_data(
                    DataType.DOCUMENT_HEADER)
            if (headers is None):
                headers = get_resolution_headers(self.PAGE_COUNT)
                self._database_source.put_data_collection(
                    {key: json.dumps(headers[key]) for key in headers})
            else:
                headers = json.loads(headers)
            self._decition_urls = {id: headers[id]['url'] for id in headers}
        except Exception:
            return False

    def get_data(self, dataId: str, dataType: DataType,
                 isNeedSaveFile=False):
        '''
        It gets data by the given id and dataType and return data.
        If there is no such data, it returns None.
        --
        Only DataType.DOCUMENT_TEXT is supported.
        '''
        if (not isinstance(dataType, DataType)):
            raise TypeError('dataType isn\'t instance of DataType')

        if (dataType == DataType.DOCUMENT_HEADER):
            raise ValueError("Not supported.")
        elif dataType == DataType.DOCUMENT_TEXT:
            text = load_resolution_text(self._decition_urls[dataId],
                                        dataId, self._temp_folder,
                                        isNeedReturnText=True,
                                        isNeedSaveTxtFile=isNeedSaveFile)
            self._database_source.put_data(dataId, text, dataType)
            return text
        raise ValueError("data type is not supported")

    def get_all_data(self, dataType: DataType):
        '''
        Get's list of dict of all data of the given type.
        Supported data types:
        DataType.DOCUMENT_HEADER
        DataType.DOCUMENT_TEXT
        '''
        if (not isinstance(dataType, DataType)):
            raise TypeError('dataType isn\'t instance of DataType')

        if (dataType == DataType.DOCUMENT_HEADER):
            headers = get_resolution_headers(self.PAGE_COUNT)
            self._database_source.\
                put_data_collection(headers, DataType.DOCUMENT_HEADER)
            return headers

        if (dataType == DataType.DOCUMENT_TEXT):
            return {id: self.get_data(id,
                    DataType.DOCUMENT_TEXT)
                    for id in self._decition_urls}


class LocalFileStorageSource(DataSource):
    headers = dict()
    FOLDER_NAME = 'ksrf_temp_folder'
    HEADERS_FILE_NAME = 'headers.json'

    def __init__(self):
        super().__init__('LocalFileStorage', DataSourceType.DATABASE)

    def prepare(self):
        try:
            if (not path.exists(self.FOLDER_NAME)):
                os.mkdir(self.FOLDER_NAME)
            headersFilePath = path.join(self.FOLDER_NAME,
                                        self.HEADERS_FILE_NAME)
            if (path.exists(headersFilePath)):
                with open(headersFilePath, 'rt') as headersFile:
                    self.headers = json.loads(headersFile.read())

        except:
            return False
        return True

    def get_data(self, dataId: str, dataType: DataType):
        '''
        It gets data by the given id and dataType and return data.
        If there is no such data, it returns None.
        Supported data types:
        DataType.DOCUMENT_HEADER
        DataType.DOCUMENT_TEXT
        '''
        if (not isinstance(dataType, DataType)):
            raise TypeError('dataType isn\'t instance of DataType')

        if (dataType == DataType.DOCUMENT_HEADER):
            return self.headers[id]
        elif (dataType == DataType.DOCUMENT_TEXT):
            textFileName = get_decision_filename_by_uid(dataId,
                                                        self.FOLDER_NAME)
            if (not path.exists(textFileName)):
                return None
            with open(textFileName, 'rt') as textFile:
                text = textFile.read()
            return text
        else:
            raise ValueError("Not supported data type")

    def get_all_data(self, dataType: DataType):
        '''
        Get's list of dict of all data of the given type.
        Supported data types:
        DataType.DOCUMENT_HEADER
        DataType.DOCUMENT_TEXT
        '''
        if (not isinstance(dataType, DataType)):
            raise TypeError('dataType isn\'t instance of DataType')

        if (dataType == DataType.DOCUMENT_HEADER):
            return self.headers

        if (dataType == DataType.DOCUMENT_TEXT):
            return {id: self.get_data(id,
                    DataType.DOCUMENT_TEXT)
                    for id in self.headers}
        else:
            raise ValueError("Not supported data type.")

    def put_data(self, id,  data, dataType: DataType):
        '''
        Save the data in the local file.
        Supported data types:
        DataType.DOCUMENT_HEADER
        DataType.DOCUMENT_TEXT
        '''
        if (not isinstance(dataType, DataType)):
            raise TypeError('dataType isn\'t instance of DataType')
        if (dataType == DataType.DOCUMENT_HEADER):
            self.headers[id] = data

        elif (dataType == DataType.DOCUMENT_TEXT):
            with open(
                 get_decision_filename_by_uid(
                     id, self.FOLDER_NAME)) as fileTXT:
                fileTXT.write(data)
        else:
            raise ValueError('dataType ins\t supported')

    def put_data_collection(self, dataDict, dataType: DataType):
        '''
        Iterate the given dataDict and invoke put_data for each
        elem of the dictionary.
        '''
        if (not isinstance(dataDict, dict)):
            raise TypeError('dataDict isn\'t dict')
        if (not isinstance(dataType, DataType)):
            raise TypeError('dataType isn\'t instance of DataType')
        for dataKey in dataDict:
            self.put_data(dataKey, dataDict[dataKey], dataType)
        if (dataType == DataType.DOCUMENT_HEADER):
            with open(path.join(self.FOLDER_NAME,
                      self.HEADERS_FILE_NAME),
                      'wt') as headersFile:
                headersFile.write(json.dumps(self.headers))

if __name__ == '__main__':
    print(PATH_TO_CHROME_WEB_DRIVER)
    headersOld = get_resolution_headers(2)
    print(headersOld)
    input('press any key...')
