import re
import random

# Import libs:

import urllib.request
# License: MIT License

import lxml.html
# License: BSD license; Installing: python -m pip install lxml

# Note: KoAP RF is the base act which was used for developing of this functions

_HOST = 'www.consultant.ru'
_REQHEADERS = {
    'User-Agent':
        random.choice(
            ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/68.0.3440.106 "
             "YaBrowser/18.9.1.954 Yowser/2.5 Safari/537.36",
             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
             )
        ),
    'Host': _HOST,
    'Accept-Language': 'ru-RU,ru;',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }

_SECTION_SIGN = 'Р'
_SUBSECTION_SIGN = 'ПДР'
_CHAPTER_SIGN = 'ГЛ'
_PARAGRAPH_SIGN = 'ПРГ'
_SUBPARAGRAPH_SIGN = 'ПДПРГ'
_ARTICLE_SIGN = 'СТ'
_NOTE_SIGN = 'ПР'
_PART_SIGN = 'Ч'
_ABZATS_SIGN = 'А'
_PUNKT_SIGN = 'П'
_PODPUNKT_SIGN = 'ПП'

_NOTE_NAME_PREFIX = '. Примечание '
_PART_NAME_PREFIX = '. Часть '
_PUNKT_NAME_PREFIX = '. Пункт '
_PODPUNKT_NAME_PREFIX = '. Подпункт '
_ABZATS_NAME_PREFIX = '. Абзац '

_editionPattern = re.compile(r'ред.\s+от\s+\d\d\.\d\d\.\d{4}')
_relPattern = re.compile(r'от\s+\d\d\.\d\d\.\d{4}')
_datePattern = re.compile(r'\d\d\.\d\d\.\d{4}')

_notePattern = re.compile(r'Примечани[ея][\.:\s]')

_sectionNumberPattern = re.compile(r'[A-Za-z]+(?:\.[-–—\d]+)*')
_subsectionNumberPattern = re.compile(r'(?<=Подраздел\s)\d+[-–—\.\d]*(?=\.\s)')
_paragraphNumberPattern = re.compile(r'(?<=§\s)\d+[-–—\.\d]*(?=\.\s)')
_subparagraphNumberPattern = re.compile(r'(?<=^)\d+[-–—\.\d]*(?=\.\s)')
_chapterNumberPattern = re.compile(r'\d+')
_articleNumberPattern = re.compile(r'\d+[-–—\.\d]*(?=\.\s)')

_articlesStartPattern = re.compile(r'[Сс]тать[яи]\s.*')
_articlesNumbersPattern = re.compile(
    r'(?:(?<=[Сс]татья\s)\d+[-–—\.\d]*(?=\.\s)|'
    r'(?<=[Сс]татья\s)\d+[-–—\.\d]*(?=\s)|(?<=[Сс]татья\s)\d+[-–—\.\d]*(?=\,)|'
    r'(?<=[Сс]татья\s)\d+[-–—\.\d]*(?=\)))'
    )

_partNumberPattern = _articleNumberPattern
_partNumberRangePattern = re.compile(
    r'\d+[-–—\.\d]*\s+[-–—]\s+\d+[-–—\.\d]*(?=\s)')
_partNumberRangeNumPattern = re.compile(r'\d+[-–—\.\d]*(?=\s)')
_partNumberRangeNumLastNum = re.compile(r'(?:\d+$|\d+(?=\.$))')

_punktNumberPattern = re.compile(r'\d+[-–—\.\d]*(?=\)\s)')
_punktNumberRangePattern = re.compile(
    r'\d+[-–—\.\d]*\)\s*?-\s*?\d+[-–—\.\d]*\)(?=\s)')
_punktNumberRangeNumPattern = re.compile(
    r'(?:\d+[-–—\.\d]*(?=\)\s)|\d+[-–—\.\d]*(?=\)[-–—]))')
_punktNumberRangeNumLastNum = _partNumberRangeNumLastNum

_podpunktNumberPattern = re.compile(r'[а-яa-z][-–—.а-яa-z]*(?=\)\s)')
_podpunktNumberRangePattern = re.compile(
    r'[а-яa-z][-.а-яa-z]*\)\s*?-\s*?[а-яa-z][-–—.а-яa-z]*\)(?=\s)')
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

_justNumberPattern = re.compile(r'\d+')
_justWordPattern = re.compile(r'[а-яА-я]+')

_enumerationCheckPattern = re.compile(r'[-–—:]+\s*?$')
_lastEnumElCheckPattern = re.compile(r'[\.]+\s*?$')
_endsWithDashCheckPattern = re.compile(r'[-–—]+\s*?$')


def _get_cookie(response):
    cookie = ''
    for h in response.headers._headers:
        if h[0] == 'Set-Cookie':
            cookie += h[1].split(';', maxsplit=1)[0] + '; '
    return cookie

def _get_page(url, reqHeaders, prevResponse=None, referer=None, raw=False):
    if prevResponse is not None:
        reqHeaders['Cookie'] = _get_cookie(prevResponse)
    if referer is not None:
        reqHeaders['Referer'] = referer
    req = urllib.request.Request(url, headers=reqHeaders)
    response = urllib.request.urlopen(req)
    if (response.code != 200):
        raise Exception('Something wrong. Response code is not 200')
    if not raw:
        return (lxml.html.document_fromstring(response.read()), response)
    else:
        return (response.read(), response)


def _get_subheaders_from_page(
        page, header, hKey, sign, host,
        subHeaderNumberPattern, baseHeader, absolutePath, onlyFirst=True,
        ignoreNoMatches=False):
    subElements = page.xpath('//contents/ul/li/a')
    subHeaders = {}

    doc_type = f"{header['doc_type']}/{sign}"
    for s in subElements:
        title = s.text
        text_source_url = f"http://{host}{s.attrib['href']}"
        if onlyFirst and not ignoreNoMatches:
            match = [subHeaderNumberPattern.search(s.text)[0]]
        else:
            match = subHeaderNumberPattern.findall(s.text)
        if not match and not ignoreNoMatches:
            raise Exception(f'Error: Article {hkey} subheaders cannot parsed '
                            'with regexp "{subHeaderNumberPattern.pattern}"')
        for subHeaderNum in match:
            docidLastPart = f"/{sign}-{subHeaderNum}".upper()
            docID = f"{hKey}" + docidLastPart
            subHeaders[docID] = {
                'supertype': baseHeader['supertype'],
                'doc_type': doc_type,
                'absolute_path': absolutePath + docidLastPart,
                'title': title,
                'release_date': baseHeader['release_date'],
                'text_source_url': text_source_url
                }
        #break  #!!!only while debugging
    return subHeaders


def _get_subheaders_from_header_title(
        headerTitle, headerUrl, header, hKey, sign, subhStartPattern,
        subHeaderNumbersPattern, baseHeader, absolutePath):
    subHeaders = {}
    spam = subhStartPattern.search(headerTitle)
    if spam is None:
        raise Exception(f"Error: Header {headerTitle}. "
                        "Cannot get numbers of no more valid subheaders.")
    subhNums = subHeaderNumbersPattern.findall(spam[0])
    title = headerTitle
    doc_type = f"{header['doc_type']}/{sign}"
    text_source_url = headerUrl
    for subHeaderNum in subhNums:
        docidLastPart = f"/{sign}-{subHeaderNum}".upper()
        docID = f"{hKey}" + docidLastPart
        subHeaders[docID] = {
            'supertype': baseHeader['supertype'],
            'doc_type': doc_type,
            'absolute_path': absolutePath + docidLastPart,
            'title': title,
            'release_date': baseHeader['release_date'],
            'text_source_url': text_source_url
            }
    return subHeaders


def _get_subhdrs_rngs_frm_strs_and_clear_strs_frm_them(
        header, hKey, stringList, subhSign, subhNamePrefix,
        subhNumRangePattern, subhNumRangeNumPattern,
        subhNumRangeNumLastNum, baseHeader, absolutePath):
    subhRangeStrings = []
    indexesForDeleting = []
    for i in range(len(stringList)):
        if subhNumRangePattern.match(stringList[i]) is not None:
            subhRangeStrings.append(stringList[i])
            indexesForDeleting.append(i)
    correction = 0
    for i in indexesForDeleting:
        del stringList[i-correction]
        correction += 1
    subheaders = {}
    for p in subhRangeStrings:
        strRange = subhNumRangePattern.match(p)[0]
        commonText = p.replace(strRange, '').strip()
        rangeNums = subhNumRangeNumPattern.findall(p)
        numTemplate = rangeNums[0].rstrip('\.')
        if subhNumRangeNumLastNum.search(rangeNums[0])[0].isdigit():
            first = int(subhNumRangeNumLastNum.search(rangeNums[0])[0])
            last = int(subhNumRangeNumLastNum.search(rangeNums[1])[0])

            doc_type = f"{header['doc_type']}/{subhSign}"
            text_source_url = header['text_source_url']
            for i in range(first, last+1):
                subhNum = subhNumRangeNumLastNum.sub(str(i), numTemplate)
                docidLastPart = f"/{subhSign}-{subhNum}".upper()
                docID = f"{hKey}" + docidLastPart
                title = header['title'] + subhNamePrefix + subhNum
                subheaders[docID] = {
                    'supertype': baseHeader['supertype'],
                    'doc_type': doc_type,
                    'absolute_path': absolutePath + docidLastPart,
                    'title': title,
                    'release_date': baseHeader['release_date'],
                    'text_source_url': text_source_url,
                    'text': commonText
                    }
        else:
            first = ord(subhNumRangeNumLastNum.search(rangeNums[0])[0])
            last = ord(subhNumRangeNumLastNum.search(rangeNums[1])[0])
            doc_type = f"{header['doc_type']}/{subhSign}"
            text_source_url = header['text_source_url']
            for i in range(first, last+1):
                subhNum = subhNumRangeNumLastNum.sub(chr(i), numTemplate)
                title = header['title'] + subhNamePrefix + subhNum
                docidLastPart = f"/{subhSign}-{subhNum}".upper()
                docID = f"{hKey}" + docidLastPart
                subheaders[docID] = {
                    'supertype': baseHeader['supertype'],
                    'doc_type': doc_type,
                    'absolute_path': absolutePath + docidLastPart,
                    'title': title,
                    'release_date': baseHeader['release_date'],
                    'text_source_url': text_source_url,
                    'text': commonText
                    }
    return subheaders


def _get_subheaders_indexes(stringList, subhNumPattern):
    subhIndexes = []
    for i in range(len(stringList)):
        if subhNumPattern.match(stringList[i]) is not None:
            subhIndexes.append(i)
    return subhIndexes


def _get_subheaders_from_strings_by_indexes(
        header, hKey, stringList, subhIndexes, subhSign, subhNamePrefix,
        subhNumPattern, baseHeader, absolutePath):
    subhListStringList = []
    if subhIndexes is not None:
        for i in range(len(subhIndexes)):
            try:
                subhListStringList.append(
                    stringList[subhIndexes[i]:subhIndexes[i+1]])
            except IndexError:
                subhListStringList.append(stringList[subhIndexes[i]:])
    else:
        for s in stringList:
            subhListStringList.append([s])
    subhDictStringList = {}
    subheaders = {}

    doc_type = f"{header['doc_type']}/{subhSign}"
    text_source_url = header['text_source_url']
    for i in range(len(subhListStringList)):

        if subhNumPattern is not None:
            subhNum = subhNumPattern.search(subhListStringList[i][0])[0]
        elif subhIndexes is None or len(subhIndexes) > 1:
            subhNum = str(i+1)
        else:
            subhNum = str(0)
        title = header['title'] + subhNamePrefix + subhNum
        docidLastPart = f"/{subhSign}-{subhNum}".upper()
        docID = f"{hKey}" + docidLastPart
        subhText = '\n'.join(subhListStringList[i])
        subhDictStringList[docID] = subhListStringList[i]
        subheaders[docID] = {
            'supertype': baseHeader['supertype'],
            'doc_type': doc_type,
            'absolute_path': absolutePath + docidLastPart,
            'title': title,
            'release_date': baseHeader['release_date'],
            'text_source_url': text_source_url,
            'text': subhText
            }
    return (subheaders, subhDictStringList)


def _get_subheaders_range_labeled_by_words_instead_numbers(
        allGottenHeaders, rejectingPatterns, header, hKey, stringList,
        subhSign, subhNamePrefix, subhNumPattern, baseHeader, absolutePath,
        thisFirstCall=False):
    ZABIT_NA_ABZATSI = True
    if len(stringList) == 1:
        return
    indexesStrsLabeledByWords = []
    subhNums = set()
    i = 0
    while i < len(stringList):
        if subhNumPattern.match(stringList[i]) is not None:
            subhNums.add(
                int(_justNumberPattern.search(stringList[i])[0]))
            i += 1
            continue
        eggs = False
        for pattern in rejectingPatterns:
            if pattern.match(stringList[i]) is not None:
                eggs = True
                break
        if eggs:
            i += 1
            continue
        if _rangeLabeledByWordsCheckPattern.search(stringList[i],
                                                  endpos=70) is not None:
            if (_rangeNoMoreValidAbzatsPattern.match(stringList[i]) is None and
                    _rangeLabeledByWordsCheckPattern.match(
                        stringList[i]) is None):
                print(f'Warning: Article {hKey} has a range labeled by words.')
                indexesStrsLabeledByWords.append(i)
            elif thisFirstCall and not ZABIT_NA_ABZATSI:
                numNoMoreValidAbzatsInRange = 0
                match = _abzatsNumberRangePattern.search(stringList[i])
                if match is not None:
                    nr = _justNumberPattern.findall(match[0])
                    numNoMoreValidAbzatsInRange = int(nr[1]) - int(nr[0]) + 1
                else:
                    match = _abzatsWordRangePattern.search(stringList[i])
                    if match is not None:
                        wnr = _justWordPattern.findall(match[0])
                        try:
                            numNoMoreValidAbzatsInRange = \
                                (_ordinalNumbersDict[wnr[1]] -
                                    _ordinalNumbersDict[wnr[0]] + 1)
                        except KeyError:
                            raise Exception(f"Error: Article {hKey} has range "
                                            "labeled word that no more valid "
                                            "abzats. But 'ordinalNumbersDict' "
                                            "doesn't contain some word from "
                                            "this words")
                    else:
                        raise Exception(f"Error: Article {hKey} has abzats "
                                        "range labeled by words. But program"
                                        " couldn't choose numbers from this "
                                        "range.")
                commonText = stringList[i]
                del stringList[i]
                for n in range(numNoMoreValidAbzatsInRange):
                    stringList.insert(i, commonText)
                for j in range(len(indexesStrsLabeledByWords)):
                    if indexesStrsLabeledByWords[j] > i:
                        indexesStrsLabeledByWords[j] += \
                            numNoMoreValidAbzatsInRange - 1
                i += numNoMoreValidAbzatsInRange - 1

        # next iteration:
        i += 1
    for index in indexesStrsLabeledByWords:
        try:
            if subhNumPattern.match(stringList[index+1]) is not None:
                lastNum = int(_justNumberPattern.search(stringList[index+1])[0])
                doc_type = f"{header['doc_type']}/{subhSign}"
                text_source_url = header['text_source_url']
                for num in range(1, lastNum):
                    subhNum = str(num)
                    docidLastPart = f"/{subhSign}-{subhNum}".upper()
                    docID = f"{hKey}" + docidLastPart
                    if (num not in subhNums and
                            docID not in allGottenHeaders):
                        commonText = stringList[index]
                        title = header['title'] + subhNamePrefix + subhNum
                        allGottenHeaders[docID] = {
                            'supertype': baseHeader['supertype'],
                            'doc_type': doc_type,
                            'absolute_path': absolutePath + docidLastPart,
                            'title': title,
                            'release_date': baseHeader['release_date'],
                            'text_source_url': text_source_url,
                            'text': commonText
                            }
            else:
                print(f"Warning: Article {hKey} has abzats after range"
                      " labeled by words.")
                return
                # raise Exception(f"Error: Article {hKey} has abzats after "
                #                 "range labeled by words.")
        except IndexError:
            print(f"Warning: Article {hKey} has range labeled by "
                  "words. This range is the last abzats in the "
                  "Article, so program can't get number of "
                  "subheaders.")
            return
            # raise Exception(f"Error: Article {hKey} has range labeled by "
            #                 "words. This range is the last abzats in the "
            #                 "Article, so program can't get number of "
            #                 "subheaders.")
    for index in indexesStrsLabeledByWords:
        del stringList[index]


def process_unique_subhs_abzats_together(
        header, hKey, stringList, subhIndexes, subhSign, subhNamePrefix,
        baseHeader, absolutePath):
    subheaders = {}
    abzatsDiapazonsIndexes = []
    abzatsDiapazonsIndexes1 = []
    abzatsDiapazonsIndexes2 = []
    stringToDeleteIndexes = []
    egg1 = egg2 = False
    if len(stringList[:subhIndexes[0]]) > 1:
        egg1 = True
        for i in range(subhIndexes[0]-1):
            abzatsDiapazonsIndexes1.append([i, i])
        abzatsDiapazonsIndexes1.append([subhIndexes[0]-1, len(stringList)-1])
        # raise Exception(f"Error: Article {hKey} has multiple abzats before "
        #                 "subheaders.")
    if _enumerationCheckPattern.search(
                        stringList[subhIndexes[-1]]) is None:
        if subhIndexes[-1] != len(stringList)-1:
            egg2 = True
            abzatsDiapazonsIndexes2.append([0, subhIndexes[-1]])
            for i in range(subhIndexes[-1]+1, len(stringList)):
                abzatsDiapazonsIndexes2.append([i, i])
                stringToDeleteIndexes.append(i)
        else:
            pass  # return subheaders
    elif _lastEnumElCheckPattern.search(stringList[-2]) is not None:
        pass  # checked: it works fine in nkrf
        # raise Exception(f"Error: Article {hKey} has abzats after end of "
        #                 "enumeration.")
    if egg1 and egg2:
        # raise Exception(f"Error: Article {hKey} has multiple abzats before "
        #                 "subheaders and abzats related to header after "
        #                 "subheaders simultaneously.")
        stringToDeleteIndexes = []
        abzatsDiapazonsIndexes1[-1][1] = abzatsDiapazonsIndexes2[0][1] - 1
        del abzatsDiapazonsIndexes2[0]
        abzatsDiapazonsIndexes.extend(abzatsDiapazonsIndexes1)
        abzatsDiapazonsIndexes.extend(abzatsDiapazonsIndexes2)
    elif egg1:
        abzatsDiapazonsIndexes = abzatsDiapazonsIndexes1
    else:
        abzatsDiapazonsIndexes = abzatsDiapazonsIndexes2

    doc_type = f"{header['doc_type']}/{subhSign}"
    text_source_url = header['text_source_url']
    for i in range(len(abzatsDiapazonsIndexes)):
        subhNum = str(i+1)
        title = header['title'] + subhNamePrefix + subhNum
        docidLastPart = f"/{subhSign}-{subhNum}".upper()
        docID = f"{hKey}" + docidLastPart
        subhText = '\n'.join(stringList[
            abzatsDiapazonsIndexes[i][0]:abzatsDiapazonsIndexes[i][1]+1])
        subheaders[docID] = {
            'supertype': baseHeader['supertype'],
            'doc_type': doc_type,
            'absolute_path': absolutePath + docidLastPart,
            'title': title,
            'release_date': baseHeader['release_date'],
            'text_source_url': text_source_url,
            'text': subhText
            }
    correction = 0
    for i in stringToDeleteIndexes:
        del stringList[i-correction]
        correction += 1
    return subheaders


class _BaseCode:
    CODE_URLS = (
        'http://www.consultant.ru/document/Кодекс_часть1/',
        'http://www.consultant.ru/document/Кодекс_часть2/',
        'http://www.consultant.ru/document/Кодекс_часть3/',
        )
    CODE_PREFIX = 'Аббревиатура кодекса'
    CODE_PART_SIGN = 'Часть кодекса (отдельный документ)'

    HOST = _HOST
    REQHEADERS = _REQHEADERS
        
    SECTION_SIGN = _SECTION_SIGN
    SUBSECTION_SIGN = _SUBSECTION_SIGN
    CHAPTER_SIGN = _CHAPTER_SIGN
    PARAGRAPH_SIGN = _PARAGRAPH_SIGN
    SUBPARAGRAPH_SIGN = _SUBPARAGRAPH_SIGN
    ARTICLE_SIGN = _ARTICLE_SIGN
    NOTE_SIGN = _NOTE_SIGN
    PART_SIGN = _PART_SIGN
    ABZATS_SIGN = _ABZATS_SIGN
    PUNKT_SIGN = _PUNKT_SIGN
    PODPUNKT_SIGN = _PODPUNKT_SIGN
    
    NOTE_NAME_PREFIX = _NOTE_NAME_PREFIX
    PART_NAME_PREFIX = _PART_NAME_PREFIX
    PUNKT_NAME_PREFIX = _PUNKT_NAME_PREFIX
    PODPUNKT_NAME_PREFIX = _PODPUNKT_NAME_PREFIX
    ABZATS_NAME_PREFIX = _ABZATS_NAME_PREFIX
        
    editionPattern = _editionPattern
    relPattern = _relPattern
    datePattern = _datePattern
        
    notePattern = _notePattern
        
    sectionNumberPattern = _sectionNumberPattern
    subsectionNumberPattern = _subsectionNumberPattern
    paragraphNumberPattern = _paragraphNumberPattern
    subparagraphNumberPattern = _subparagraphNumberPattern
    chapterNumberPattern = _chapterNumberPattern
    articleNumberPattern = _articleNumberPattern
        
    articlesStartPattern = _articlesStartPattern
    articlesNumbersPattern = _articlesNumbersPattern
        
    partNumberPattern = _partNumberPattern
    partNumberRangePattern = _partNumberRangePattern
    partNumberRangeNumPattern = _partNumberRangeNumPattern
    partNumberRangeNumLastNum = _partNumberRangeNumLastNum
        
    punktNumberPattern = _punktNumberPattern
    punktNumberRangePattern = _punktNumberRangePattern
    punktNumberRangeNumPattern = _punktNumberRangeNumPattern
    punktNumberRangeNumLastNum = _punktNumberRangeNumLastNum
        
    podpunktNumberPattern = _podpunktNumberPattern
    podpunktNumberRangePattern = _podpunktNumberRangePattern
    podpunktNumberRangeNumPattern = _podpunktNumberRangeNumPattern
    podpunktNumberRangeNumLastNum = _podpunktNumberRangeNumLastNum

    loneNoMoreValidAbzatsPattern = _loneNoMoreValidAbzatsPattern

    lastEnumElCheckPattern = _lastEnumElCheckPattern
    endsWithDashCheckPattern = _endsWithDashCheckPattern

    @classmethod
    def get_code_content(cls):
        codeHeaders = {}
        for i in range(len(cls.CODE_URLS)):
            if len(cls.CODE_URLS) > 1:
                # debug print
                print(f"\n{cls.CODE_PREFIX} {cls.CODE_PART_SIGN} {i+1}/{len(cls.CODE_URLS)}:")
                doc_type = f"{cls.CODE_PREFIX}/{cls.CODE_PART_SIGN}"
                cls.CODE_PART_KEY = f"{cls.CODE_PREFIX}/{cls.CODE_PART_SIGN}-{str(i+1)}"
            else:
                # debug print
                print(f"\n{cls.CODE_PREFIX}:")
                doc_type = cls.CODE_PREFIX
                cls.CODE_PART_KEY = cls.CODE_PREFIX
            
            supertype = cls.CODE_PREFIX
            code_URL = cls.CODE_URLS[i]
            codeMainPage, response = _get_page(code_URL, cls.REQHEADERS)
            title = codeMainPage.xpath('//h1')[0].text

            # getting page with title
            spam1 = {'doc_type': cls.CODE_PREFIX}
            spam2 = {
                'supertype': '',
                'release_date': '',
                }
            spam3 = _get_subheaders_from_page(
                codeMainPage, spam1, cls.CODE_PREFIX,
                cls.SECTION_SIGN, cls.HOST, cls.sectionNumberPattern, spam2, cls.CODE_PREFIX)

            # getting true code part title:
            pageWithTitle, spam = _get_page(
                list(spam3.values())[0]['text_source_url'], cls.REQHEADERS)
            title = pageWithTitle.xpath('//b[@id="documentTitleLink"]')[0].text

            releaseDateMatch = cls.editionPattern.search(title)
            if releaseDateMatch is None:
                releaseDateMatch = cls.relPattern.search(title)
                if releaseDateMatch is None:
                    raise Exception('Cannot parse release date')
            release_date = cls.datePattern.search(releaseDateMatch[0])[0]

            text_source_url = code_URL

            codeHeaders[cls.CODE_PART_KEY] = {
                'supertype': supertype,
                'doc_type': doc_type,
                'absolute_path': cls.CODE_PART_KEY,
                'title': title,
                'release_date': release_date,
                'text_source_url': text_source_url
                }

            baseHeader = {
                'supertype': supertype,
                'release_date': release_date,
                }

            # start of sections processing
            headerWithcodeDocType = {'doc_type': cls.CODE_PREFIX}
            sectionHeaders = _get_subheaders_from_page(
                codeMainPage, headerWithcodeDocType, cls.CODE_PREFIX,
                cls.SECTION_SIGN, cls.HOST, cls.sectionNumberPattern, baseHeader,
                codeHeaders[cls.CODE_PART_KEY]['absolute_path'])
            codeHeaders.update(sectionHeaders)
            # end of sections processing

            # start of chapters and subsections processing
            chapterHeaders = {}
            shdKeys = list(sectionHeaders.keys())
            while shdKeys:
                key = shdKeys[0]
                codeSectionPage, response = _get_page(
                    sectionHeaders[key]['text_source_url'], cls.REQHEADERS,
                    response, codeHeaders[cls.CODE_PART_KEY]['text_source_url']
                    )
                subsectionsTemp = _get_subheaders_from_page(
                    codeSectionPage, sectionHeaders[key], key,
                    cls.SUBSECTION_SIGN, cls.HOST, cls.subsectionNumberPattern, baseHeader,
                    sectionHeaders[key]['absolute_path'], ignoreNoMatches=True
                    )
                if subsectionsTemp:
                    codeHeaders.update(subsectionsTemp)
                    sectionHeaders.update(subsectionsTemp)
                    del sectionHeaders[key]
                    shdKeys.extend(subsectionsTemp.keys())
                else:
                    temp = _get_subheaders_from_page(
                            codeSectionPage, headerWithcodeDocType, cls.CODE_PREFIX,
                            cls.CHAPTER_SIGN, cls.HOST, cls.chapterNumberPattern, baseHeader,
                            sectionHeaders[key]['absolute_path'], 
                            )
                    chapterHeaders.update(temp)
                del shdKeys[0]
            codeHeaders.update(chapterHeaders)
            # end of chapters and subsections processing

            # start of first stage of articles processing
            articleHeaders = {}
            chphKeys = list(chapterHeaders.keys())
            #testURL = 'http://www.consultant.ru/document/cons_doc_LAW_5142/783f9943d8039ff2e742ea93a317d52393568c0b/'
            #chapterHeaders[chphKeys[0]]['text_source_url'] = testURL
            while chphKeys:
                key = chphKeys[0]
                codeChapterPage, response = _get_page(
                    chapterHeaders[key]['text_source_url'], cls.REQHEADERS,
                    response, codeHeaders[cls.CODE_PART_KEY]['text_source_url']
                    )
                paragraphsTemp = _get_subheaders_from_page(
                    codeChapterPage, chapterHeaders[key], key,
                    cls.PARAGRAPH_SIGN, cls.HOST, cls.paragraphNumberPattern, baseHeader,
                    chapterHeaders[key]['absolute_path'], ignoreNoMatches=True
                    )
                if paragraphsTemp:
                    codeHeaders.update(paragraphsTemp)
                    chapterHeaders.update(paragraphsTemp)
                    del chapterHeaders[key]
                    chphKeys.extend(paragraphsTemp.keys())
                else:
                    subparagraphsTemp = _get_subheaders_from_page(
                        codeChapterPage, chapterHeaders[key], key,
                        cls.SUBPARAGRAPH_SIGN, cls.HOST, cls.subparagraphNumberPattern, baseHeader,
                        chapterHeaders[key]['absolute_path'], ignoreNoMatches=True
                        )
                    if subparagraphsTemp:
                        codeHeaders.update(subparagraphsTemp)
                        chapterHeaders.update(subparagraphsTemp)
                        del chapterHeaders[key]
                        chphKeys.extend(subparagraphsTemp.keys())
                    else:
                        ahs = _get_subheaders_from_page(
                                codeChapterPage, headerWithcodeDocType, cls.CODE_PREFIX,
                                cls.ARTICLE_SIGN, cls.HOST, cls.articlesNumbersPattern, baseHeader,
                                chapterHeaders[key]['absolute_path'], onlyFirst=False
                                )
                        if ahs:
                            articleHeaders.update(ahs)
                        else:
                            print(f"Warning: Chapter {key} is no more valid.")
                            ahs = _get_subheaders_from_header_title(
                                chapterHeaders[key]['title'],
                                chapterHeaders[key]['text_source_url'],
                                headerWithcodeDocType, cls.CODE_PREFIX,
                                cls.ARTICLE_SIGN, cls.articlesStartPattern,
                                cls.articlesNumbersPattern, baseHeader,
                                chapterHeaders[key]['absolute_path']
                            )
                            if ahs:
                                articleHeaders.update(ahs)
                            else:
                                raise Exception(f"Cannot get articles from chapter {key}")
                del chphKeys[0]
            codeHeaders.update(articleHeaders)
            # end of first stage of articles processing

            # start of last stage of articles processing
            # start of parts processing
            numArt = 1  # debug
            for key in articleHeaders:
                print(f'Processing article {numArt}/{len(articleHeaders)}...',
                    end='\r')  # debug
                numArt += 1  # debug
                # testURL = 'testUrl'
                #testURL = 'http://www.consultant.ru/document/cons_doc_LAW_34661/ebf5dddb0d5fcdf25d19cbc40c405fc254be2f76/'
                #articleHeaders[key]['text_source_url'] = testURL
                codeArticlePage, response = _get_page(
                    articleHeaders[key]['text_source_url'], cls.REQHEADERS,
                    response,
                    codeHeaders[cls.CODE_PART_KEY]['text_source_url']
                    )
                try:
                    textTitle = codeArticlePage.xpath(
                        '//div[@class="text"]/h1/div[@style]/span')[0].\
                            text_content()
                except IndexError:
                    textTitle = codeArticlePage.xpath('//h1')[0].text_content()
                codeHeaders[key]['title'] = textTitle
                stringList = []
                spans = codeArticlePage.xpath(
                    '//div[@class="text"]/div[@style]/span')
                for string in spans:
                    string_text = string.text_content()
                    if string_text != '\xa0':
                        stringList.append(string_text)
                articleText = textTitle + '\n\n' + '\n'.join(stringList)
                codeHeaders[key]['text'] = articleText
                # end of article processing

                # start of notes processing
                noteStrings = []
                for i in range(len(stringList)):
                    if cls.notePattern.match(stringList[i]) is not None:
                        noteStrings = stringList[i:]
                        del stringList[i:]
                        break
                # In the future, it will be necessary
                # to expand the processing of notes.
                if noteStrings:
                    noteHeaders = _get_subheaders_from_strings_by_indexes(
                        articleHeaders[key], key, noteStrings, [0], cls.NOTE_SIGN,
                        cls.NOTE_NAME_PREFIX, None, baseHeader,
                        articleHeaders[key]['absolute_path']
                        )[0]
                    codeHeaders.update(noteHeaders)
                # end of notes processing

                codeHeaders.update(
                    _get_subhdrs_rngs_frm_strs_and_clear_strs_frm_them(
                        articleHeaders[key], key, stringList, cls.PART_SIGN,
                        cls.PART_NAME_PREFIX, cls.partNumberRangePattern,
                        cls.partNumberRangeNumPattern, cls.partNumberRangeNumLastNum,
                        baseHeader, articleHeaders[key]['absolute_path']
                        )
                    )

                _get_subheaders_range_labeled_by_words_instead_numbers(
                    codeHeaders, [cls.punktNumberPattern, cls.punktNumberRangePattern,
                                cls.podpunktNumberPattern,
                                cls.podpunktNumberRangePattern,
                                cls.loneNoMoreValidAbzatsPattern],
                    articleHeaders[key], key, stringList, cls.PART_SIGN,
                    cls.PART_NAME_PREFIX,  cls.partNumberPattern, baseHeader, 
                    articleHeaders[key]['absolute_path'], thisFirstCall=True
                    )

                partsIndexes = _get_subheaders_indexes(stringList,
                                                    cls.partNumberPattern)
                if not partsIndexes:
                    if (len(stringList) > 1 and
                            cls.lastEnumElCheckPattern.search(
                                stringList[0]) is not None):
                        abzatsHeaders = _get_subheaders_from_strings_by_indexes(
                                articleHeaders[key], key, stringList, None,
                                cls.ABZATS_SIGN, cls.ABZATS_NAME_PREFIX, None, baseHeader,
                                articleHeaders[key]['absolute_path']
                                )[0]
                        codeHeaders.update(abzatsHeaders)
                        continue
                    else:
                        continue

                partHeaders, partsDictStringList = \
                    _get_subheaders_from_strings_by_indexes(
                        articleHeaders[key], key, stringList, partsIndexes,
                        cls.PART_SIGN, cls.PART_NAME_PREFIX, cls.partNumberPattern, baseHeader,
                        articleHeaders[key]['absolute_path']
                        )
                codeHeaders.update(partHeaders)

                # start of punkts processing
                for key in partHeaders:
                    codeHeaders.update(
                        _get_subhdrs_rngs_frm_strs_and_clear_strs_frm_them(
                            partHeaders[key], key, partsDictStringList[key],
                            cls.PUNKT_SIGN, cls.PUNKT_NAME_PREFIX, cls.punktNumberRangePattern,
                            cls.punktNumberRangeNumPattern, cls.punktNumberRangeNumLastNum,
                            baseHeader, partHeaders[key]['absolute_path']
                            )
                        )

                    _get_subheaders_range_labeled_by_words_instead_numbers(
                        codeHeaders, [cls.podpunktNumberPattern,
                                    cls.podpunktNumberRangePattern,
                                    cls.partNumberPattern,
                                    cls.loneNoMoreValidAbzatsPattern],
                        partHeaders[key], key, partsDictStringList[key],
                        cls.PUNKT_SIGN, cls.PUNKT_NAME_PREFIX, cls.punktNumberPattern,
                        baseHeader, partHeaders[key]['absolute_path']
                        )

                    punktIndexes = _get_subheaders_indexes(partsDictStringList[key],
                                                        cls.punktNumberPattern)

                    # just need to check on big dataset
                    if (len(partsDictStringList[key]) > 2 and
                            cls.endsWithDashCheckPattern.search(
                                partsDictStringList[key][0]) is not None):
                        print(f"Warning: Part {key} has multiple abzats after '-',"
                            " please check.")

                    if not punktIndexes:
                        if (len(partsDictStringList[key]) > 1 and
                                cls.endsWithDashCheckPattern.search(
                                    partsDictStringList[key][0]) is None):
                            abzatsHeaders = _get_subheaders_from_strings_by_indexes(
                                partHeaders[key], key, partsDictStringList[key],
                                None, cls.ABZATS_SIGN, cls.ABZATS_NAME_PREFIX, None,
                                baseHeader, partHeaders[key]['absolute_path']
                                )[0]
                            codeHeaders.update(abzatsHeaders)
                        else:
                            continue
                    else:
                        codeHeaders.update(
                            process_unique_subhs_abzats_together(
                                partHeaders[key], key, partsDictStringList[key],
                                punktIndexes, cls.ABZATS_SIGN, cls.ABZATS_NAME_PREFIX,
                                baseHeader, partHeaders[key]['absolute_path']
                                )
                            )

                        punktHeaders, punktsDictStringList = \
                            _get_subheaders_from_strings_by_indexes(
                                partHeaders[key], key, partsDictStringList[key],
                                punktIndexes, cls.PUNKT_SIGN, cls.PUNKT_NAME_PREFIX,
                                cls.punktNumberPattern, baseHeader,
                                partHeaders[key]['absolute_path']
                                )
                        codeHeaders.update(punktHeaders)

                        # avos'
                        # start of podpunkts processing
                        for key in punktHeaders:
                            codeHeaders.update(
                                _get_subhdrs_rngs_frm_strs_and_clear_strs_frm_them(
                                    punktHeaders[key], key,
                                    punktsDictStringList[key],
                                    cls.PODPUNKT_SIGN, cls.PODPUNKT_NAME_PREFIX,
                                    cls.podpunktNumberRangePattern,
                                    cls.podpunktNumberRangeNumPattern,
                                    cls.podpunktNumberRangeNumLastNum, baseHeader,
                                    punktHeaders[key]['absolute_path']
                                    )
                                )
                            podpunktIndexes = _get_subheaders_indexes(
                                punktsDictStringList[key], cls.podpunktNumberPattern)

                            # just need to check on big dataset
                            if (len(punktsDictStringList[key]) > 2 and
                                    cls.endsWithDashCheckPattern.search(
                                        punktsDictStringList[key][0]) is not None):
                                print(f"Warning: Punkt {key} has multiple abzats "
                                    "after '-', please check.")

                            if not podpunktIndexes:
                                if len(punktsDictStringList[key]) > 1 and \
                                        cls.endsWithDashCheckPattern.search(
                                            punktsDictStringList[key][0]) is None:
                                    abzatsHeaders = \
                                        _get_subheaders_from_strings_by_indexes(
                                            punktHeaders[key], key,
                                            punktsDictStringList[key], None,
                                            cls.ABZATS_SIGN, cls.ABZATS_NAME_PREFIX,
                                            None, baseHeader,
                                            punktHeaders[key]['absolute_path']
                                            )[0]
                                    codeHeaders.update(abzatsHeaders)
                                else:
                                    continue
                            else:
                                codeHeaders.update(
                                    process_unique_subhs_abzats_together(
                                        punktHeaders[key], key,
                                        punktsDictStringList[key], podpunktIndexes,
                                        cls.ABZATS_SIGN, cls.ABZATS_NAME_PREFIX, baseHeader,
                                        punktHeaders[key]['absolute_path']
                                        )
                                    )

                                podpunktHeaders, podpunktsDictStringList = \
                                    _get_subheaders_from_strings_by_indexes(
                                        punktHeaders[key], key,
                                        punktsDictStringList[key], podpunktIndexes,
                                        cls.PODPUNKT_SIGN, cls.PODPUNKT_NAME_PREFIX,
                                        cls.podpunktNumberPattern, baseHeader,
                                        punktHeaders[key]['absolute_path']
                                        )
                                codeHeaders.update(podpunktHeaders)
                                for key in podpunktHeaders:
                                    if len(podpunktsDictStringList[key]) > 1 and \
                                        cls.endsWithDashCheckPattern.search(
                                            podpunktsDictStringList[key][0]) \
                                            is None:
                                        abzatsHeaders = \
                                            _get_subheaders_from_strings_by_indexes(
                                                podpunktHeaders[key], key,
                                                podpunktsDictStringList[key], None,
                                                cls.ABZATS_SIGN, cls.ABZATS_NAME_PREFIX,
                                                None, baseHeader,
                                                podpunktHeaders[key]['absolute_path']
                                                )[0]
                                        codeHeaders.update(abzatsHeaders)
                                    else:
                                        continue
                        # end of podpunkts processing
                # end of punkts processing
            # end of last stage of articles processing
            # end of parts processing
        # end of code processing
        return codeHeaders


class _Koaprf(_BaseCode):
    CODE_URLS = (
        'http://www.consultant.ru/document/cons_doc_LAW_34661',)
    CODE_PREFIX = 'КОАПРФ'


class _Nkrf (_BaseCode):
    CODE_URLS = (
        'http://www.consultant.ru/document/cons_doc_LAW_19671',
        'http://www.consultant.ru/document/cons_doc_LAW_28165')
    CODE_PREFIX = 'НКРФ'
    CODE_PART_SIGN = 'Ч'

    PART_SIGN = _PUNKT_SIGN
    PART_NAME_PREFIX = _PUNKT_NAME_PREFIX
    PUNKT_SIGN = _PODPUNKT_SIGN
    PUNKT_NAME_PREFIX = _PODPUNKT_NAME_PREFIX
    PODPUNKT_SIGN = _ABZATS_SIGN
    PODPUNKT_NAME_PREFIX = _ABZATS_NAME_PREFIX


class _Gkrf(_BaseCode):
    CODE_URLS = (
        'http://www.consultant.ru/document/cons_doc_LAW_5142/',
        'http://www.consultant.ru/document/cons_doc_LAW_9027/',
        'http://www.consultant.ru/document/cons_doc_LAW_34154/',
        'http://www.consultant.ru/document/cons_doc_LAW_64629/'
        )
    CODE_PREFIX = 'ГКРФ'
    CODE_PART_SIGN = 'Ч'

    PART_SIGN = _PUNKT_SIGN
    PART_NAME_PREFIX = _PUNKT_NAME_PREFIX
    PUNKT_SIGN = _PODPUNKT_SIGN
    PUNKT_NAME_PREFIX = _PODPUNKT_NAME_PREFIX
    PODPUNKT_SIGN = _ABZATS_SIGN
    PODPUNKT_NAME_PREFIX = _ABZATS_NAME_PREFIX


_codesParsers = {
    'КОАПРФ': _Koaprf,
    'НКРФ': _Nkrf,
    'ГКРФ': _Gkrf
}

_ALL_CODES = frozenset(_codesParsers.keys())

def get_content(codes: set=_ALL_CODES):
    if hasattr(codes, '__iter__'):
        if isinstance(codes, str) and codes in _ALL_CODES:
            codes = {codes}
        else:
            eggs = True
            for code in codes:
                if code not in _ALL_CODES:
                    eggs = False
                    break
            if not eggs:
                raise ValueError("Elements of 'codes' must be string from "
                                 f"list: {list(_codesParsers.keys())}")
    else:
        raise TypeError(f"'Codes' must be iterable structure with {type(str)} "
                        "as elements.")
    codesContent = {}
    for code in codes:
        codeContent = _codesParsers[code].get_code_content()
        codesContent.update(codeContent)
    return codesContent

if __name__ == '__main__':
    import os
    import json
    import time
    start_time = time.time()
    #codes = {'КОАПРФ', 'НКРФ', 'ГКРФ'}
    codes = {'КОАПРФ'}
    # codes = 'КОАПРФ'
    # codes = {'НКРФ'}
    # codes = {'ГКРФ'}
    codeHeaders = get_content(codes)
    print(f"\nCodes processing spent {time.time()-start_time} seconds.\n"
          f"Total IDs: {len(codeHeaders)}.")
    pathToFile = f'{list(codes)[0]}_codeHeaders.json'
    dirname = os.path.dirname(pathToFile)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(pathToFile, 'w', encoding='utf-8') as jsonFile:
        json.dump(codeHeaders, jsonFile)
    input("press any key...")
    # pathToFile = 'online.json'
    # with open(pathToFile, 'rt', encoding='utf-8') as jsonFile:
    #     jsonOLD = json.load(jsonFile)
    # pathToFile1 = 'online (1).json'
    # with open(pathToFile1, 'rt', encoding='utf-8') as jsonFile1:
    #     jsonNEW = json.load(jsonFile1)
    # oldkeys = jsonOLD.keys()
    # newkeys = jsonNEW.keys()
    # ab = oldkeys - newkeys
    # ba = newkeys - oldkeys
    # print(1)