# coding: utf-8
import os
from platform import system as system_name
from subprocess import call as system_call
import json
import re
import math

# Import libs:

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

PATH_TO_CHROME_WEB_DRIVER = (os.path.dirname(__file__) +
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
                   pageUri=KSRF_PAGE_URI):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(pathToChromeWebDriver, chrome_options=options)
    driver.get(pageUri)
    return driver


def get_open_page_script_template(
        driver: 'selenium.webdriver.chrome.webdriver.WebDriver',
        templateKey='NUMBER'):
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


def get_decision_headers(pagesNumber=None, sourcePrefix='КСРФ'):
    # TO DO: check for that page is refreshed
    courtSiteContent = {}
    driver = get_web_driver()
    template = get_open_page_script_template(driver)
    page = html.document_fromstring(driver.page_source)
    if pagesNumber is None:
        decisionsNumPerPage = len(page.find_class('ms-alternating') +
                                  page.find_class('ms-vb'))
        pagesNumber = get_pages_number(page, decisionsNumPerPage)

    for i in range(2, pagesNumber + 2):
        decisions = page.find_class('ms-alternating') + \
                page.find_class('ms-vb')
        for d in decisions:
            key = d[2].text_content().replace(' ', '').upper()
            decisionID = sourcePrefix + '/' + key
            docType = sourcePrefix + '/' + typePattern.search(key)[0]
            date = d[0].text_content()
            title = d[1].text_content()
            url = d[2].getchildren()[0].get('href')
            headerElements = {'release_date': date, 'doc_type': docType,
                              'title': title, 'text_source_url': url}
            if decisionID not in courtSiteContent:
                courtSiteContent[decisionID] = headerElements
            else:
                if 'not unique' in courtSiteContent[decisionID]:
                    eggs = False
                    for header in courtSiteContent[decisionID][1]:
                        if header['text_source_url'] == url:
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


def get_possible_text_location(docID, folderName, ext='txt'):
    return os.path.join(folderName, docID.replace('/', '_') + '.' + ext)


def download_decision_text(url, docID, folderName, needSaveTxtFile=False,
                           needReturnText=False):
    if not needSaveTxtFile and not needReturnText:
        raise ValueError("'needSaveTxtFile' and 'needReturnText' cannot be"
                         " equal to False at the same time")
    logo = urllib.request.urlopen(url).read()
    pathToPDF = get_possible_text_location(docID, folderName, 'pdf')
    pathToTXT = get_possible_text_location(docID, folderName, 'txt')
    with open(pathToPDF, "wb") as PDFFIle:
        PDFFIle.write(logo)
    with open(pathToPDF, "rb") as PDFFIle, \
            open(pathToTXT, 'wb') as TXTFile:
        pdfminer.high_level.extract_text_to_fp(PDFFIle, TXTFile)
    with open(pathToTXT, 'rt', encoding='utf-8') as TXTFile:
        text = TXTFile.read()
    os.remove(pathToPDF)
    if (needSaveTxtFile and needReturnText):
        return (pathToTXT, text)
    elif needReturnText:
        return text
    else:
        return pathToTXT


def download_decision_texts(courtSiteContent, folderName='Decision files'):
    # TO DO: check for downloading and converting
    if not os.path.exists(folderName):
        os.mkdir(folderName)
    for decisionID in courtSiteContent:
        if 'not unique' in courtSiteContent[decisionID]:
            continue
        pathToTXT = download_decision_text(
                courtSiteContent[decisionID]['text_source_url'],
                decisionID, folderName)
        courtSiteContent[decisionID]['text_location'] = pathToTXT
    return courtSiteContent


def get_pages_number(page=None, elemOnPage=20):
    if page is None:
        driver = get_web_driver()
        page = html.document_fromstring(driver.page_source)
        elemOnPage = len(page.find_class('ms-alternating') +
                         page.find_class('ms-vb'))
        driver.quit()
    countOfElem = int(page.find_class('ms-formlabel')[0].
                      getchildren()[1].text_content().
                      split(':')[1].strip())
    return math.ceil(countOfElem / elemOnPage)


class KSRFSource(DataSource):
    _temp_folder = 'ksrf_temp_folder'
    _decision_urls = dict()
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
                headers = get_decision_headers()
                self._database_source.put_data_collection(
                    {key: json.dumps(headers[key]) for key in headers})
            else:
                headers = json.loads(headers)
            self._decision_urls = {docID: headers[docID]['text_source_url']
                                   for docID in headers}
        except Exception:
            return False

    def get_data(self, dataId: str, dataType: DataType):
        '''
        It gets data by the given id and dataType and return data.
        If there is no such data, it returns None.
        --
        Only DataType.DOCUMENT_TEXT is supported.
        '''
        if (not isinstance(dataType, DataType)):
            raise TypeError('dataType isn\'t instance of DataType')
        if dataType == DataType.DOCUMENT_TEXT:
            text = self._database_source.get_data(dataId, dataType)
            if (text is None):
                text = download_decision_text(self._decition_urls[dataId],
                                              dataId, self._temp_folder,
                                              needReturnText=True)
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
            headers = get_decision_headers()
            self._database_source.\
                put_data_collection(headers, DataType.DOCUMENT_HEADER)
            return headers

        if (dataType == DataType.DOCUMENT_TEXT):
            return {dataId: self.get_data(id,
                    DataType.DOCUMENT_TEXT)
                    for dataId in self._decition_urls}
        raise ValueError("data type is not supported")


class LocalFileStorageSource(DataSource):
    headers = dict()
    FOLDER_NAME = 'ksrf_temp_folder'
    HEADERS_FILE_NAME = 'headers.json'

    def __init__(self):
        super().__init__('LocalFileStorage', DataSourceType.DATABASE)

    def prepare(self):
        try:
            if (not os.path.exists(self.FOLDER_NAME)):
                os.mkdir(self.FOLDER_NAME)
            headersFilePath = os.path.join(self.FOLDER_NAME,
                                           self.HEADERS_FILE_NAME)
            if (os.path.exists(headersFilePath)):
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
            return self.headers[dataId]
        elif (dataType == DataType.DOCUMENT_TEXT):
            textFileName = get_possible_text_location(dataId, self.FOLDER_NAME)
            if (not os.path.exists(textFileName)):
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
            return {docID: self.get_data(docID, DataType.DOCUMENT_TEXT)
                    for docID in self.headers}
        else:
            raise ValueError("Not supported data type.")

    def put_data(self, docID,  data, dataType: DataType):
        '''
        Save the data in the local file.
        Supported data types:
        DataType.DOCUMENT_HEADER
        DataType.DOCUMENT_TEXT
        '''
        if (not isinstance(dataType, DataType)):
            raise TypeError('dataType isn\'t instance of DataType')
        if (dataType == DataType.DOCUMENT_HEADER):
            self.headers[docID] = data

        elif (dataType == DataType.DOCUMENT_TEXT):
            with open(
                 get_possible_text_location(
                     docID, self.FOLDER_NAME)) as fileTXT:
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
            with open(os.path.join(self.FOLDER_NAME,
                      self.HEADERS_FILE_NAME),
                      'wt') as headersFile:
                headersFile.write(json.dumps(self.headers))

if __name__ == '__main__':
    headersOld = get_decision_headers()
    print(headersOld)
    input('press any key...')
