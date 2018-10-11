import os.path

import urllib.request
# License: MIT License

import pdfminer.high_level
# License: MIT License; Installing: python -m pip install pdfminer.six

import lxml.html as html
# License: BSD license; Installing: python -m pip install lxml

from selenium import webdriver
# License: Apache License 2.0


PATH_TO_CHROME_WEB_DRIVER = 'web_crawler\\Selenium\\chromedriver.exe'
KSRF_PAGE_URI = 'http://www.ksrf.ru/ru/Decision/Pages/default.aspx'


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


def get_resolution_headers(countOfPage=1):
    # TO DO: check for that page is refreshed
    courtSiteContent = {}
    driver = get_web_driver()
    template = get_open_page_script_template(driver)
    page = html.document_fromstring(driver.page_source)
    for i in range(2, countOfPage + 2):
        decisions = page.find_class('ms-alternating') + \
                page.find_class('ms-vb')
        for d in decisions:
            decisionID = d[2].text_content().replace(' ', '').upper()
            date = d[0].text_content()
            title = d[1].text_content()
            url = d[2].getchildren()[0].get('href')
            headerElements = {'date': date, 'url': url, 'title': title}
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


def load_resolution_texts(courtSiteContent, folderName='Decision files'):
    # TO DO: check for downloading and converting
    if not os.path.exists(folderName):
        os.mkdir(folderName)
    for decisionID in courtSiteContent:
        if 'not unique' in courtSiteContent[decisionID]:
            continue
        logo = urllib.request.urlopen(
                courtSiteContent[decisionID]['url']).read()
        pathToPDF = get_decision_filename_by_uid(decisionID, folderName, 'pdf')
        pathToTXT = get_decision_filename_by_uid(decisionID, folderName, 'txt')
        with open(pathToPDF, "wb") as PDFFIle:
            PDFFIle.write(logo)
        with open(pathToPDF, "rb") as PDFFIle, \
                open(pathToTXT, 'wb') as TXTFile:
            pdfminer.high_level.extract_text_to_fp(PDFFIle, TXTFile)
        courtSiteContent[decisionID]['path to text file'] = pathToTXT
        os.remove(pathToPDF)
    return courtSiteContent
