# Web Crawler

## Установка
 
 1. Установить [whl файл](https://github.com/robot-lab/judyst-web-crawler/blob/IntenseWeek/dist/web_crawler-0.1-py3-none-any.whl)
 
 ### Использование
 
 Перед работой с модулем желательно выполнить инициализацию модуля источником данных. Источником данных может являться любой объект, следующий интерфейсу web_crawler.DataSource 

Следующий код показывает, как инициализировать web_crawler для работы с базой данных.  "точкой соединения" с базой данных является объект [ModelData](https://github.com/robot-lab/judyst-main-web-service/blob/master/celery/data.py)
 
 ```
from web_crawler import Init_by_data_model
from data import ModelData
model = ModelData()
Init_by_data_model(databaseSource = model)
...
 ```
 
Если Вы хотит просто использовать web_crawler для извлечения данных из базы данных, Вам не обязательно инициализировать весь модуль. Можно инициализировать только ресурс базы данных, это можно сделать так:
 
 ```
from web_crawler import DatabaseWrapper
from data import ModelData
model = ModelData()
source = DatabaseWrapper("name", model)
source.get_data("КСРФ/2483-О/2018")
...
 ```
