__version__ = '0.1'

if __package__:
    from web_crawler import ksrf
    from web_crawler.web_crawler import WebCrawler
    from web_crawler.web_crawler\
        import DataSource, DataSourceType, DataType
    Database_Source = ksrf.LocalFileStorageSource()
    KSRF_Source = ksrf.KSRFSource(Database_Source)

    Crawler = WebCrawler([Database_Source, KSRF_Source])
    __all__ = ['Crawler', 'DataSourceType', 'DataType', 'KSRF_Source']
