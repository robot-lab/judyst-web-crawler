import re
import random

# Import libs:

import urllib.request
# License: MIT License

import lxml.html
# License: BSD license; Installing: python -m pip install lxml

# Note: KoAP RF is the base act which was used for developing of this functions

HOST = 'www.consultant.ru'
REQHEADERS = {
    'User-Agent':
        random.choice(
            ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/68.0.3440.106 '
                'YaBrowser/18.9.1.954 Yowser/2.5 Safari/537.36',
             )
        ),
    'Host': HOST,
    'Accept-Language': 'ru;q=0.9',
    'Accept': 'text/html;q=0.8'
    }

SECTION_SIGN = 'Р'
SUBSECTION_SIGN = 'ПДР'
CHAPTER_SIGN = 'ГЛ'
PARAGRAPH_SIGN = 'ПРГ'
SUBPARAGRAPH_SIGN = 'ПДПРГ'
ARTICLE_SIGN = 'СТ'
NOTE_SIGN = 'ПР'
PART_SIGN = 'Ч'
ABZATS_SIGN = 'А'
PUNKT_SIGN = 'П'
PODPUNKT_SIGN = 'ПП'
NOTE_NAME_PREFIX = '. Примечание '
PART_NAME_PREFIX = '. Часть '
PUNKT_NAME_PREFIX = '. Пункт '
ABZATS_NAME_PREFIX = '. Абзац '
PODPUNKT_NAME_PREFIX = '. Подпункт '

editionPattern = re.compile(r'ред.\s+от\s+\d\d\.\d\d\.\d{4}')
relPattern = re.compile(r'от\s+\d\d\.\d\d\.\d{4}')
datePattern = re.compile(r'\d\d\.\d\d\.\d{4}')

notePattern = re.compile(r'Примечани[ея][\.:\s]')

sectionNumberPattern = re.compile(r'[A-Za-z]+(?:\.[-–—\d]+)*')
subsectionNumberPattern = re.compile(r'(?<=Подраздел\s)\d+[-–—\.\d]*(?=\.\s)')
paragraphNumberPattern = re.compile(r'(?<=§\s)\d+[-–—\.\d]*(?=\.\s)')
subparagraphNumberPattern = re.compile(r'(?<=^)\d+[-–—\.\d]*(?=\.\s)')
chapterNumberPattern = re.compile(r'\d+')
articleNumberPattern = re.compile(r'\d+[-–—\.\d]*(?=\.\s)')

articlesStartPattern = re.compile(r'[Сс]тать[яи]\s.*')
articlesNumbersPattern = re.compile(
    r'(?:(?<=[Сс]татья\s)\d+[-–—\.\d]*(?=\.\s)|'
    r'(?<=[Сс]татья\s)\d+[-–—\.\d]*(?=\s)|(?<=[Сс]татья\s)\d+[-–—\.\d]*(?=\,)|'
    r'(?<=[Сс]татья\s)\d+[-–—\.\d]*(?=\)))'
    )

partNumberPattern = articleNumberPattern
partNumberRangePattern = re.compile(
    r'\d+[-–—\.\d]*\s+[-–—]\s+\d+[-–—\.\d]*(?=\s)')
partNumberRangeNumPattern = re.compile(r'\d+[-–—\.\d]*(?=\s)')
partNumberRangeNumLastNum = re.compile(r'(?:\d+$|\d+(?=\.$))')

punktNumberPattern = re.compile(r'\d+[-–—\.\d]*(?=\)\s)')
punktNumberRangePattern = re.compile(
    r'\d+[-–—\.\d]*\)\s*?-\s*?\d+[-–—\.\d]*\)(?=\s)')
punktNumberRangeNumPattern = re.compile(
    r'(?:\d+[-–—\.\d]*(?=\)\s)|\d+[-–—\.\d]*(?=\)[-–—]))')
punktNumberRangeNumLastNum = partNumberRangeNumLastNum

podpunktNumberPattern = re.compile(r'[а-яa-z][-–—.а-яa-z]*(?=\)\s)')
podpunktNumberRangePattern = re.compile(
    r'[а-яa-z][-.а-яa-z]*\)\s*?-\s*?[а-яa-z][-–—.а-яa-z]*\)(?=\s)')
podpunktNumberRangeNumPattern = re.compile(
    r'(?:[а-яa-z][-–—.а-яa-z]*(?=\)\s)|[а-яa-z][-–—.а-яa-z]*(?=\)-))')
podpunktNumberRangeNumLastNum = re.compile(r'[а-яa-z]+$')

rangeLabeledByWordsCheckPattern = re.compile(
    r'(?:[Уу]тратил(?:[аи]|)\s*?силу|[Ии]сключен(?:[аы]|)\s)')
loneNoMoreValidAbzatsPattern = re.compile(r'^\s*?[аА]бзац\s')
rangeNoMoreValidAbzatsPattern = re.compile(r'^\s*?[аА]бзацы\s')
abzatsNumberRangePattern = re.compile(
    r'(?<=[а-яА-я]\s)\s*?\d+\s*?[-–—]\s*?\d+')
abzatsWordRangePattern = re.compile(
    r'(?<=[а-яА-я]\s)\s*?[а-яА-я]+\s*?[-–—]\s*?[а-яА-я]+')

ordinalNumbersDict = {
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

justNumberPattern = re.compile(r'\d+')
justWordPattern = re.compile(r'[а-яА-я]+')

enumerationCheckPattern = re.compile(r'[-–—:]+\s*?$')
lastEnumElCheckPattern = re.compile(r'[\.]+\s*?$')
endsWithDashCheckPattern = re.compile(r'[-–—]+\s*?$')


def get_cookie(response):
    cookie = ''
    for h in response.headers._headers:
        if h[0] == 'Set-Cookie':
            cookie += h[1].split(';', maxsplit=1)[0] + '; '
    return cookie


def get_page(url, reqHeaders, prevResponse=None, referer=None):
    if prevResponse is not None:
        reqHeaders['Cookie'] = get_cookie(prevResponse)
    if referer is not None:
        reqHeaders['Referer'] = referer
    req = urllib.request.Request(url, headers=reqHeaders)
    response = urllib.request.urlopen(req)
    if (response.code != 200):
        raise Exception('Something wrong. Response code is not 200')
    return (lxml.html.document_fromstring(response.read()), response)


def get_subheaders_from_page(
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


def get_subheaders_from_header_title(
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


def get_subhdrs_rngs_frm_strs_and_clear_strs_frm_them(
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


def get_subheaders_indexes(stringList, subhNumPattern):
    subhIndexes = []
    for i in range(len(stringList)):
        if subhNumPattern.match(stringList[i]) is not None:
            subhIndexes.append(i)
    return subhIndexes


def get_subheaders_from_strings_by_indexes(
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


def get_subheaders_range_labeled_by_words_instead_numbers(
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
                int(justNumberPattern.search(stringList[i])[0]))
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
        if rangeLabeledByWordsCheckPattern.search(stringList[i],
                                                  endpos=70) is not None:
            if (rangeNoMoreValidAbzatsPattern.match(stringList[i]) is None and
                    rangeLabeledByWordsCheckPattern.match(
                        stringList[i]) is None):
                print(f'Warning: Article {hKey} has a range labeled by words.')
                indexesStrsLabeledByWords.append(i)
            elif thisFirstCall and not ZABIT_NA_ABZATSI:
                numNoMoreValidAbzatsInRange = 0
                match = abzatsNumberRangePattern.search(stringList[i])
                if match is not None:
                    nr = justNumberPattern.findall(match[0])
                    numNoMoreValidAbzatsInRange = int(nr[1]) - int(nr[0]) + 1
                else:
                    match = abzatsWordRangePattern.search(stringList[i])
                    if match is not None:
                        wnr = justWordPattern.findall(match[0])
                        try:
                            numNoMoreValidAbzatsInRange = \
                                (ordinalNumbersDict[wnr[1]] -
                                    ordinalNumbersDict[wnr[0]] + 1)
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
                lastNum = int(justNumberPattern.search(stringList[index+1])[0])
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
    if enumerationCheckPattern.search(
                        stringList[subhIndexes[-1]]) is None:
        if subhIndexes[-1] != len(stringList)-1:
            egg2 = True
            abzatsDiapazonsIndexes2.append([0, subhIndexes[-1]])
            for i in range(subhIndexes[-1]+1, len(stringList)):
                abzatsDiapazonsIndexes2.append([i, i])
                stringToDeleteIndexes.append(i)
        else:
            pass  # return subheaders
    elif lastEnumElCheckPattern.search(stringList[-2]) is not None:
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
