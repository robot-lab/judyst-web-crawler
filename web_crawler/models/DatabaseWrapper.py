import os

import json
if __package__:
    from web_crawler.web_crawler import DataSource,\
        DataType, DataSourceType 


class DatabaseWrapper(DataSource):
    source = None
    DOCUMENTS = 'Documents'
    LINKS = 'Links'
    DOCUMENT_FIELDS = ['supertype', 'doc_type','title',
                       'release_date' , 'text_source_url',
                       'effective_date','absolute_path',
                       'interredaction_id', 'cons_selected_info']
    LINK_FIELDS = ['doc_id_from', 'doc_id_to', 'positions_list', 'citations_number']
    def __init__(self, name, dataSource):
        super().__init__(name, DataSourceType.DATABASE)
        self.source = dataSource
    
    def prepare(self):
        return True

    def _request_fields(self, retDict, fieldNames, modelName, doc_id):
        for fieldName in fieldNames:
            retDict[fieldName] = self.source.\
                                      get_data(fieldName,
                                               model_name=modelName,
                                               doc_id=doc_id)


    def _prepare_data(self, data, fieldsNames):
        fieldName = 'positions_list'
        if  fieldName in fieldsNames and fieldName in data.keys():
            data['citations_number'] = len(data[fieldName])
            data[fieldName] = [json.dumps(data[fieldName][i]) for i in range(len(data[fieldName]))]

        fieldName = 'cons_selected_info'
        if fieldName in fieldsNames and fieldName in data.keys():
            data[fieldName] = json.dumps(data[fieldName])

        return data


    def _create_data(self, dataDict, fieldNames, modelName, **requireKwargs):
        data = dict()
        for fieldName in fieldNames:
            if fieldName in dataDict.keys():
                data[fieldName] = dataDict[fieldName]
        data = self._prepare_data(data, fieldNames)
        self.source.create_data(model_name=modelName, **data,
                                **requireKwargs)


    def _edit_data(self, dataDict, fieldNames, modelName, **requireKwargs):
        data = dict()
        for fieldName in fieldNames:
            if fieldName in dataDict.keys():
                data[fieldName] = dataDict[fieldName]
        data = self._prepare_data(data, fieldNames)
        self.source.edit_data(data, model_name=modelName, **requireKwargs)


    def get_data(self, dataId, dataType):
        if (dataType == DataType.DOCUMENT_HEADER):
            model_name = self.DOCUMENTS
            header = dict()
            self._request_fields(header, self.DOCUMENT_FIELDS, 
                                 model_name, dataId)            
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
            modelName = self.DOCUMENTS
            if (self.source.get_data('doc_id', model_name=self.DOCUMENTS,
                                     doc_id=docId) is None):
                self._create_data(data, self.DOCUMENT_FIELDS,
                                  modelName, doc_id=docId)
            else:
                self._edit_data(data, self.DOCUMENT_FIELDS, modelName, doc_id=docId)
            return

        if (dataType == DataType.LINK):
            modelName = self.LINKS
            doc_id_from = data['doc_id_from']
            doc_id_to = data['doc_id_to']
            if (self.source.get_data('doc_id_from', model_name=self.LINKS,
                                    doc_id_from=doc_id_from,
                                    doc_id_to=doc_id_to) is None):                                   
               self._create_data(data, self.LINK_FIELDS, modelName)
            else:
                self._edit_data(data, self.LINK_FIELDS, modelName,
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
        