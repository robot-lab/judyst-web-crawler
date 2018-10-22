from web_crawler.ksrf import *
from web_crawler.web_crawler import *


def main():
    localStorage = LocalFileStorageSource()
    localStorage.prepare()
    webSource = KSRFWebSource(localStorage)
    webSource.PAGE_COUNT = 1
    headers = webSource.get_all_data(DataType.DOCUMENT_HEADER)
    print(headers)
    print(localStorage.get_data('КСРФ_36-П_2017', DataType.DOCUMENT_TEXT))


main()
