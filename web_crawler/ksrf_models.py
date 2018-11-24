import os

import json
if __package__:
    # retrorsum compatibility
    from web_crawler.models.DatabaseWrapper import DatabaseWrapper as KSRFDatabaseWrapper
    from web_crawler.models.KSRFSource import *
    from web_crawler.models.LocalFileStorageSource import *
else:
    models.LocalFileStorageSource import *
    models.KSRFSource import *
    models.DatabaseWrapper import *




