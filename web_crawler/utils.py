import json
import os

from web_crawler.web_crawler import DataType

DOCUMENT_FIELDS = ['supertype', 'doc_type',' title',
                    'release_date', 'text', 'text_source_url',
                    'effective_date',' absolute_path',
                    'interredaction_id', 'cons_selected_info']
                    
LINK_FIELDS = ['doc_id_from', 'doc_id_to', 'positions_list', 'citations_number']




def fill_data_source_from_file(dataSource, fields, fileName):
    f = open(fileName,'r', encoding='utf-8')
    for line in f:
        header = json.loads(line); 
        doc_id = header.keys()[0]
        header = header[doc_id]
        dataSource.put_data(doc_id, header, DataType.DOCUMENT_HEADER)

