from enum import Enum


class DataType(Enum):
    '''
    Types of data.
    '''
    DOCUMENT_HEADER = 0
    DOCUMENT_TEXT = 1
    ANALYZIS_RESULT = 2


class DataSourceType(Enum):
    '''
    Types of data sources.
    '''
    DATABASE = 0
    WEB_SOURCE = 1


class DataSource:
    '''
    Abstract representation of data source.
    For using you need an inheritor.
    '''
    source_type = -1
    source_name = 'Unnamed'

    def __init__(self, name, sourceType):
        if (not isinstance(name, str)):
            raise TypeError('name should be a str')
        if (name == ''):
            raise ValueError('name shouldn\'t be empty')
        if (not isinstance(sourceType, DataSourceType)):
            raise TypeError('sourceType should be\
               selected from DataSourceType enum')
        self.source_name = name
        self.source_type = sourceType

    def get_data(self, dataId: str, dataType: DataType):
        '''
        It gets data by the given id and dataType and return data.
        If there is no such data, it returns None.
        It must be overwritten.
        '''
        raise Exception('Abstract method invoked.')

    def get_all_data(self, dataType: DataType):
        '''
        Get's all data of the given type.
        It must be overwritten.
        '''
        raise Exception('Abstract method invoked.')

    def prepare(self):
        '''
        It try to prepare the data source for work and
        return False if preparing have failed.
        It return True if all is ok.
        It must be overwritten.
        '''
        raise Exception('Abstract method invoked.')

    def __eq__(self, other):
        if (not isinstance(other, DataSource)):
            raise TypeError('other should be an instance of DataSource')
        return self.source_name == other.source_name

    def __ne__(self, value):
        return not self.__eq__(value)

    def __hash__(self):
        return 9221288222353123 + self.source_name.__hash__() +\
            self.source_type.__hash__()


class WebCrawler:
    '''
    WebCrawler is a wrapper around
    multiple data source.
    It functions is only to manage data source.
    For requesting any data use DataSource types.
    '''
    available_sources = dict()

    def get_data_source(self, name: str):
        '''
        Return the data source by it's name.
        '''
        if (name in self.available_sources):
            return self.available_sources[name]
        else:
            return None

    def __init__(self, dataSources: list):
        '''
        It try to initialize all existing data sources and
        choose for available_source sources which is
        succesffully prepared for work.
        '''
        for dataSource in dataSources:
            if (not isinstance(dataSource, DataSource)):
                raise TypeError('dataSources\'s elements should be\
                    instances of DataSource class')
            res = dataSource.prepare()
            if (dataSource.source_name in self.available_sources):
                raise ValueError('names of the data sources should be unique.')
            if (res):
                self.available_sources[dataSource.name] = dataSource
