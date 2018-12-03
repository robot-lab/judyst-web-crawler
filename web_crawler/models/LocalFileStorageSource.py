import os
import json

if __package__:
    from web_crawler.web_crawler import DataSource,\
        DataType, DataSourceType 
    from web_crawler.ksrf import *


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
                headersFile.write(json.dumps(self.headers))
