import os

import json
if __package__:
    from web_crawler.web_crawler import DataSource,\
        DataType, DataSourceType 
    from web_crawler.ksrf import *
else:
    from web_crawler import DataSource,\
        DataType, DataSourceType 
    from ksrf import *


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
            # TODO repair site available check
            # res = ping(KSRF_PAGE_URI)
            # if (not res):
            #    return False
            # Error: too many headers in database. TODO fix it. 
            # headersFromBase = self._database_source.get_all_data(
            #         DataType.DOCUMENT_HEADER)
            
            # if (headersFromBase is None or len(headersFromBase) == 0):
            #     headers = get_decision_headers()
            #     self._database_source.\
            #         put_data_collection(headers,
            #                             DataType.DOCUMENT_HEADER)
            # else:
            #     headers = headersFromBase

            # self._decision_urls = {}
            # for dataId in headers:
            #     elem = headers[dataId]
            #     self._decision_urls[dataId] = elem['text_source_url']
            return True
        except Exception as e:
            print(e)
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
