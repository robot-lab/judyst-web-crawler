
import time
if __package__:
    from web_crawler.web_crawler import DataType
else:
    from web_crawler import DataType

def split_dup_headers(headers):
    pass


def updatae_database_from_source(databaseSource, source, supertype='KSRF'):
    '''
    Update documents in databaseSource by documents from source
    '''

    if (supertype == 'KSRF'):
        print(time.time)
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

