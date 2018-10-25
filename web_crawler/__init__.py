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
Database_Source = ksrf.LocalFileStorageSource()
KSRF_Source = ksrf.KSRFSource(Database_Source)
Crawler = WebCrawler([Database_Source, KSRF_Source])
# Crawler.collected_sources['LocalFileStorage'].folder_path = \
#     'D:\\programming\\Judyst\\files'
# Crawler.prepare_sources(['LocalFileStorage', 'KSRFSource'])

# Crawler.prepare_sources()
# source = Crawler.get_data_source('KSRFsource')
__all__ = ['Crawler', 'DataSourceType', 'DataType', 'KSRF_Source']
