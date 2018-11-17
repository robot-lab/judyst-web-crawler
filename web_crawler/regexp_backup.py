_editionPattern = re.compile(r'ред.\s+от\s+\d\d\.\d\d\.\d{4}')
_relPattern = re.compile(r'от\s+\d\d\.\d\d\.\d{4}')
_notePattern = re.compile(r'Примечани[ея][\.:\s]')
_articlesStartPattern = re.compile(r'[Сс]тать[яи]\s.*')


_partNumberRangeNumPattern = re.compile(r'\d+(?:\.[-–—\d]+)*(?=\s)')
_partNumberRangeNumLastNum = re.compile(r'(?:\d+$|\d+(?=\.$))')


_punktNumberRangeNumPattern = re.compile(
    r'(?:\d+(?:\.[-–—\d]+)*(?=\)\s)|\d+(?:\.[-–—\d]+)*(?=\)[-–—]))')
_punktNumberRangeNumLastNum = _partNumberRangeNumLastNum


_podpunktNumberRangeNumPattern = re.compile(
    r'(?:[а-яa-z][-–—.а-яa-z]*(?=\)\s)|[а-яa-z][-–—.а-яa-z]*(?=\)-))')
_podpunktNumberRangeNumLastNum = re.compile(r'[а-яa-z]+$')

_rangeLabeledByWordsCheckPattern = re.compile(
    r'(?:[Уу]тратил(?:[аи]|)\s*?силу|[Ии]сключен(?:[аы]|)\s)')

_loneNoMoreValidAbzatsPattern = re.compile(r'^\s*?[аА]бзац\s')

_rangeNoMoreValidAbzatsPattern = re.compile(r'^\s*?[аА]бзацы\s')
_abzatsNumberRangePattern = re.compile(
    r'(?<=[а-яА-я]\s)\s*?\d+\s*?[-–—]\s*?\d+')
_abzatsWordRangePattern = re.compile(
    r'(?<=[а-яА-я]\s)\s*?[а-яА-я]+\s*?[-–—]\s*?[а-яА-я]+')

_ordinalNumbersDict = {
    'первый': 1,
    'второй': 2,
    'третий': 3,
    'четвертый': 4,
    'четвёртый': 4,
    'пятый': 5,
    'шестой': 6,
    'седьмой': 7,
    'восьмой': 8,
    'девятый': 9,
    'десятый': 10,
    'одиннадцатый': 11,
    'двенадцатый': 12,
    'тринадцатый': 13,
    'четырнадцатый': 14,
    'пятнадцатый': 15,
    'шестнадцатый': 16,
    'семнадцатый': 17,
    'восемнадцатый': 18,
    'двадцатый': 20
}


_enumerationCheckPattern = re.compile(r'[-–—:]+\s*?$')
_lastEnumElCheckPattern = re.compile(r'[\.]+\s*?$')
_endsWithDashCheckPattern = re.compile(r'[-–—]+\s*?$')
