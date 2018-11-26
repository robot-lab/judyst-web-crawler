# encoding: 'utf-8'
import time
import json

if __package__:
    from web_crawler.web_crawler import DataType
else:
    from web_crawler import DataType

DOCUMENT_FIELDS = ['supertype', 'doc_type','title',
                       'release_date' , 'text_source_url',
                       'effective_date','absolute_path',
                       'interredaction_id', 'cons_selected_info']
                    
LINK_FIELDS = ['doc_id_from', 'doc_id_to', 'positions_list', 'citations_number']


FILE_FORMATS = ['jsonlines', 'json']

def fill_data_source_from_file(dataSource, fileName,
                               fileFormat='jsonlines',
                               dataType=DataType.DOCUMENT_HEADER):
    f = open(fileName,'rt', encoding='utf-8')
    if (fileFormat == FILE_FORMATS[0]):
        if (dataType == DataType.LINK):
            for line in f:
                link = json.loads(line)
                dataSource.put_data('', link, dataType)           
        else:
            for line in f:
                header = json.loads(line)
                doc_id = list(header.keys())[0]
                header = header[doc_id]
                dataSource.put_data(doc_id, header, dataType)
    elif fileFormat == FILE_FORMATS[1]:
        if (dataType == DataType.LINK):
            links = json.loads(f.read())
            for link in links:
                dataSource.put_data('', link, dataType)
        else:
            headers = json.loads(f.read())
            for doc_id in headers:
                dataSource.put_data(doc_id, headers[doc_id], dataType)
    f.close()


def split_dup_headers(headers):
    pass


def updatae_database_from_source(databaseSource, source, supertype='KSRF'):
    '''
    Update documents in databaseSource by documents from source
    '''

    if (supertype == 'KSRF'):
        print(time.time())
        print('Start updating... ')
        headers = source.get_all_data(DataType.DOCUMENT_HEADER)
        print(f'headers length: {len(headers)}')
        databaseSource.put_data_collection(headers,
                                            DataType.DOCUMENT_HEADER)
        print('headers loaded')
        for uid in headers:
            text = source.get_data(uid, DataType.DOCUMENT_TEXT)
            databaseSource.put_data(uid, text, DataType.DOCUMENT_TEXT)
            print(f'uid {uid} puted.')
        print(time.time)
        print('all done')

