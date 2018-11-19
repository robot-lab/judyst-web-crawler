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


class KSRFDatabaseWrapper(DataSource):
    source = None
    DOCUMENTS = 'Documents'
    LINKS = 'Links'
    def __init__(self, name, dataSource):
        super().__init__(name, DataSourceType.DATABASE)
        self.source = dataSource
    
    def prepare(self):
        return True

    def get_data(self, dataId, dataType):
        if (dataType == DataType.DOCUMENT_HEADER):
            super_type = self.source.get_data('super_type',
                                              model_name=self.DOCUMENTS,
                                              doc_id=dataId)
            release_date = self.source.get_data('release_date',
                                                model_name=self.DOCUMENTS,
                                                doc_id=dataId)
            doc_type = self.source.get_data('doc_type',
                                            model_name=self.DOCUMENTS,
                                            doc_id=dataId)
            title = self.source.get_data('title',
                                         model_name=self.DOCUMENTS,
                                         doc_id=dataId)
            text_source_url = self.source.get_data('text_source_url',
                                            model_name=self.DOCUMENTS,
                                            doc_id=dataId)
            header = {'supertype':super_type,
                        'release_date':release_date, 
                        'doc_type':doc_type,
                        'title':title,
                        'text_source_url':text_source_url
                        }
            return header
        if (dataType == DataType.DOCUMENT_TEXT):
            text = self.source.get_data('text',
                                              model_name=self.DOCUMENTS,
                                              doc_id=dataId)
            return text
        
        raise ValueError('Not supported data type')


    def get_all_data(self, dataType):
        uids = self.source.get_all_data('doc_id',
                                        model_name=self.DOCUMENTS,
                                        )
        if (dataType == DataType.DOCUMENT_HEADER or
                dataType == DataType.DOCUMENT_TEXT):
            ret = {}
            for uid in uids:
                ret[uid] = self.get_data(uid, dataType)
            return ret
        
        raise ValueError('Not supported data type')
    

    def put_data(self, docId, data, dataType):
        if (dataType == DataType.DOCUMENT_HEADER):
            
            super_type = data['supertype']
            release_date = data['release_date']
            doc_type = data['doc_type']
            title = data['title']
            text_source_url = data['text_source_url']
            
            if (self.source.get_data('doc_id', model_name=self.DOCUMENTS,
                                     doc_id=docId) is None):
                self.source.create_data(model_name=self.DOCUMENTS,
                                        doc_id=docId, super_type=super_type,
                                 release_date=release_date,
                                 doc_type=doc_type, title=title,
                                 text_source_url=text_source_url)
            else:
                self.source.edit_data(
                                       {'doc_id': docId,
                                       'super_type': super_type,
                                       'release_date': release_date,
                                       'doc_type': doc_type,
                                       'title': title,
                                       'text_source_url': text_source_url
                                       },model_name=self.DOCUMENTS,
                                       doc_id=docId)
            return

        if (dataType == DataType.LINK):
            doc_id_from = data['doc_id_from']
            doc_id_to = data['doc_id_to']
            citations_number = len(data['positions_list'])
            # positions_list = [json.dumps(data['positions_list'][i])  for i in range(citations_number)]
            positions_list = data['positions_list']
            if (self.source.get_data('doc_id_from', model_name=self.LINKS,
                                    doc_id_from=doc_id_from,
                                    doc_id_to=doc_id_to) is None):                                   
                self.source.create_data(model_name=self.LINKS,
                                        doc_id_from=doc_id_from,
                                        doc_id_to=doc_id_to,
                                        citations_number=citations_number,
                                        positions_list=[json.dumps(positions_list[i]) for i in range(len(positions_list))])
            else:
                self.source.edit_data(
                                        {'doc_id_from': doc_id_from,
                                        'doc_id_to': doc_id_to,
                                        'citations_number': citations_number,
                                        'positions_list': [json.dumps(positions_list[i]) for i in range(len(positions_list))]},
                                        model_name=self.LINKS,
                                        doc_id_from=doc_id_from,
                                        doc_id_to=doc_id_to)
            return    

        if (dataType == DataType.DOCUMENT_TEXT):
            if (self.source.get_data('doc_id', model_name=self.DOCUMENTS,
                                     doc_id=docId is None)):                                   
                self.source.create_data(model_name=self.DOCUMENTS,
                                        doc_id=docId,
                                        text=data)
            else:
                self.source.edit_data({'text':data},
                                       model_name=self.DOCUMENTS,
                                       doc_id=docId
                                     )
            return    
        
        raise ValueError('Not supported data type')
        
    def put_data_collection(self, dataCollection, dataType):
        if (dataType == DataType.DOCUMENT_HEADER or
                dataType == DataType.DOCUMENT_TEXT):
            for uid in dataCollection:
                self.put_data(uid, dataCollection[uid], dataType)
            return
        if (dataType == DataType.LINK):
            for link in dataCollection:
                self.put_data('', link, DataType.LINK)
            return
        raise ValueError('Not supported data type')
        