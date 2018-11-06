__version__ = '0.1'

if __package__:
    from web_crawler import ksrf
    from web_crawler.web_crawler import WebCrawler
    from web_crawler.web_crawler\
        import DataSource, DataSourceType, DataType
else:
    import ksrf
    from web_crawler import WebCrawler
    from web_crawler\
        import DataSource, DataSourceType, DataType
Local_database_source = ksrf.LocalFileStorageSource()
KSRF_Source = ksrf.KSRFSource()
Crawler = WebCrawler([Local_database_source, KSRF_Source])


def Init(sourceNameList=None, databaseSource=None):
    '''
    Initialize web_crawler for working. 
    Should be invoked before any actions with
    Crawler
    '''
    global Crawler
    Crawler.prepare_sources(sourceNameList, databaseSource)
# Local_database_source.folder_path = 'D:\\programming\\Judyst\\files'
# Local_database_source.prepare()
# Init(databaseSource=Local_database_source)

__all__ = ['Crawler', 'DataSourceType', 'DataType', 'Init']
