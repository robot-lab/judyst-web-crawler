__version__ = '0.1'

if __package__:
    from web_crawler import ksrf_models, tools
    from web_crawler.web_crawler import WebCrawler
    from web_crawler.web_crawler\
        import DataSource, DataSourceType, DataType
    from web_crawler.models.DatabaseWrapper import DatabaseWrapper
else:
    import ksrf_models
    from web_crawler import WebCrawler
    from web_crawler\
        import DataSource, DataSourceType, DataType
Local_database_source = ksrf_models.LocalFileStorageSource()
KSRF_Source = ksrf_models.KSRFSource()
Crawler = WebCrawler([Local_database_source, KSRF_Source])


def Init(sourceNameList=None, databaseSource=None):
    '''
    Initialize web_crawler for working.
    Should be invoked before any actions with
    Crawler
    '''
    global Crawler
    Crawler.prepare_sources(sourceNameList, databaseSource)

def Init_by_data_model(sourceNameList=None, databaseSource=None):
    '''
    Initialize web_crawler for working.
    Should be invoked before any actions with
    Crawler
    '''
    global Crawler
    Crawler.prepare_sources(
        databaseSource=DatabaseWrapper('DatabaseSource', databaseSource))
        
def Init_by_KSRF_wrapper(dataModels):
    '''
    Initialize web_crawler for working. 
    Should be invoked before any actions with
    Crawler.
    Activate KSRF_Source and KSRF_database sources
    '''
    wrapper_name = 'KSRFDatabase'
    wrapper = ksrf_models.KSRFDatabaseWrapper(wrapper_name,
                                                  dataModels)   
    Crawler.collected_sources[wrapper_name] = wrapper
    Crawler.prepare_sources([wrapper_name, 'KSRFSource'], wrapper)


# Local_database_source.folder_path = 'D:\\programming\\Judyst\\files'
# Local_database_source.prepare()
# Init(databaseSource=Local_database_source)

__all__ = ['Crawler', 'DataSourceType', 'DataType',
           'Init', 'Init_by_data_model', 'DatabaseWrapper']
