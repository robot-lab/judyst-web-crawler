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


if system_name().lower() == 'windows':
    PATH_TO_CHROME_WEB_DRIVER = os.path.join(os.path.dirname(__file__),
                             'Selenium','chromedriver.exe')
else:
    PATH_TO_CHROME_WEB_DRIVER = os.path.join(os.path.dirname(__file__),
                             'Selenium','chromedriver')



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
            title = d[1].text_content()
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
            print(f"Pages downloaded: {i-1}/{pagesNumber}")
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

if __name__ == '__main__':
    headersOld = get_decision_headers()
    print(headersOld)
    input('press any key...')
