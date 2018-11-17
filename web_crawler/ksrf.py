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

PATH_TO_CHROME_WEB_DRIVER = os.path.join(os.path.dirname(__file__),
                             'Selenium','chromedriver.exe')
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
        driver,
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

pdfNumberPattern = re.compile(r"(?<=[A-Za-z])\d+")


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

    dupDict = {}
    for i in range(2, pagesNumber + 2):
        decisions = page.find_class('ms-alternating') + \
                page.find_class('ms-vb')
        for d in decisions:
            key = d[2].text_content().replace(' ', '').upper()
            decisionID = sourcePrefix + '/' + key
            docType = sourcePrefix + '/' + typePattern.search(key)[0]
            date = d[0].text_content()
            title = d[1].text_content().strip()
            url = d[2].getchildren()[0].get('href')
            headerElements = {'supertype': sourcePrefix,
                              'release_date': date, 'doc_type': docType,
                              'title': title, 'text_source_url': url}
            if decisionID not in courtSiteContent and\
                    decisionID not in dupDict:
                courtSiteContent[decisionID] = headerElements
            else:
                if decisionID not in dupDict:
                    alreadyAddedUrl = courtSiteContent[decisionID][
                        'text_source_url']
                    alreadyAddedNewDecID = decisionID\
                        + f'/{pdfNumberPattern.search(alreadyAddedUrl)[0]}-DUP'
                    dupDict[decisionID] = [courtSiteContent[decisionID]]
                    courtSiteContent[alreadyAddedNewDecID] = courtSiteContent[
                        decisionID]
                    del courtSiteContent[decisionID]
                eggs = False
                for header in dupDict[decisionID]:
                    if header['text_source_url'] == url:
                        eggs = True
                        break
                if not eggs:
                    newDecID = decisionID + \
                        f'/{pdfNumberPattern.search(url)[0]}-DUP'
                    dupDict[decisionID].append(headerElements)
                    courtSiteContent[newDecID] = headerElements
        page = html.document_fromstring(get_page_html_by_num(
                                                        driver, template, i))
        if True:  # debug print:
            print(f"Pages downloaded: {i-1}/{pagesNumber}", end='\r')
    driver.quit()
    return courtSiteContent


def get_possible_text_location(docID, folderName, ext='txt'):
    return os.path.join(folderName, docID.replace('/', '_') + '.' + ext)

pageNumberPattern = re.compile(r"""(?:(?i)\x0c\s*\d+|\x0c(?=\s)|
                               (?i)\x0c\s*$)""", re.VERBOSE)


def del_NP_and_pageNums(textForProccessing):
    text = pageNumberPattern.sub('', textForProccessing)
    return text


def download_text(url, docID, folderName, needSaveTxtFile=False,
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
        rawText = TXTFile.read()
    text = pageNumberPattern.sub('', rawText)
    os.remove(pathToPDF)
    if (needSaveTxtFile and needReturnText):
        return (pathToTXT, text)
    elif needReturnText:
        return text
    else:
        return pathToTXT


def download_all_texts(courtSiteContent, folderName='Decision files',
                       needSaveTxtFile=True):
    # TO DO: check for downloading and converting
    if not os.path.exists(folderName):
        os.mkdir(folderName)
    for decisionID in courtSiteContent:
        if 'not unique' in courtSiteContent[decisionID]:
            continue
        pathToTXT = download_text(
                courtSiteContent[decisionID]['text_source_url'],
                decisionID, folderName, needSaveTxtFile=True)
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

    def __init__(self):
        super().__init__('KSRFSource', DataSourceType.WEB_SOURCE)

    def set_database(self, database):
        '''
        set given database data source to the data source
        '''
        self._database_source = database

    def prepare(self):
        '''
        It try to prepare the data source for work and
        return False if preparing have failed.
        It return True if all is ok.
        '''
        try:
            # res = ping(KSRF_PAGE_URI)
            # if (not res):
            #    return False
            headersFromBase = self._database_source.get_all_data(
                    DataType.DOCUMENT_HEADER)
            if (headersFromBase is None or len(headersFromBase) == 0):
                headers = get_decision_headers()
                self._database_source.\
                    put_data_collection(headers,
                                        DataType.DOCUMENT_HEADER)
            else:
                headers = headersFromBase

            self._decision_urls = {}
            for dataId in headers:
                elem = headers[dataId]
                self._decision_urls[dataId] = elem['text_source_url']
            return True
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
                text = download_text(self._decision_urls[dataId],
                                     dataId, self._temp_folder,
                                     needReturnText=True)
                self._database_source.put_data(dataId, text, dataType)
            return text
        raise ValueError("data type is not supported")

    def get_all_data(self, dataType: DataType, needReload=False):
        '''
        Get's list of dict of all data of the given type.
        Supported data types:
        DataType.DOCUMENT_HEADER
        DataType.DOCUMENT_TEXT
        '''
        if (not isinstance(dataType, DataType)):
            raise TypeError('dataType isn\'t instance of DataType')

        if (dataType == DataType.DOCUMENT_HEADER):
            if (needReload):
                headers = get_decision_headers()
                self._database_source.\
                    put_data_collection(headers, DataType.DOCUMENT_HEADER)
            else:
                headers = self._database_source.get_all_data(
                          DataType.DOCUMENT_HEADER)
                if (headers is None or len(headers) == 0):
                    headers = get_decision_headers()
                    self._database_source.\
                        put_data_collection(headers, DataType.DOCUMENT_HEADER)
            return headers

        if (dataType == DataType.DOCUMENT_TEXT):
            return {dataId: self.get_data(id,
                    DataType.DOCUMENT_TEXT)
                    for dataId in self._decision_urls}
        raise ValueError("data type is not supported")


class LocalFileStorageSource(DataSource):
    headers = dict()
    folder_path = 'ksrf_temp_folder'
    HEADERS_FILE_NAME = 'DecisionHeaders.json'

    def __init__(self):
        super().__init__('LocalFileStorage', DataSourceType.DATABASE)

    def prepare(self):
        try:
            if (not os.path.exists(self.folder_path)):
                os.mkdir(self.folder_path)
            headersFilePath = os.path.join(self.folder_path,
                                           self.HEADERS_FILE_NAME)
            if (os.path.exists(headersFilePath)):
                with open(headersFilePath, 'rt', encoding='utf-8')\
                        as headersFile:
                    headers = json.loads(headersFile.read())
                    self.headers = {uid: headers[uid]
                                    for uid in headers
                                    if 'not unique' not in headers[uid]}

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
            textFileName = get_possible_text_location(dataId, self.folder_path)
            if (not os.path.exists(textFileName)):
                text = download_text(self.headers[dataId]['text_source_url'],
                                     dataId, self.folder_path, True, True)[1]
            with open(textFileName, 'rt', encoding='utf-8') as textFile:
                text = textFile.read()

            if text is None:
                raise ValueError("Can't get text")
            else:
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
            if (len(self.headers) > 0):
                return self.headers
            else:
                return None

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
                     docID, self.folder_path), 'wt', encoding='utf-8')\
                     as fileTXT:
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
            with open(os.path.join(self.folder_path,
                      self.HEADERS_FILE_NAME),
                      'wt', encoding='utf-8') as headersFile:
                headersFile.write(json.dumps(self.headers, ensure_ascii=False))

if __name__ == '__main__':
    headersOld = get_decision_headers()
    print(headersOld)
    input('press any key...')
