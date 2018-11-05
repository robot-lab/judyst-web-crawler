import re
import random

# Import libs:

import urllib.request
# License: MIT License

import lxml.html
# License: BSD license; Installing: python -m pip install lxml

HOST = 'www.consultant.ru'
CODEX_URL = 'http://www.consultant.ru/document/cons_doc_LAW_34661'
CODEX_PREFIX = 'КОАПРФ'
SECTION_SIGN = 'Р'
CHAPTER_SIGN = 'ГЛ'
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

upperLevelKeyPattern = re.compile(r'.*(?=/)')
sectionNumberPattern = re.compile(r'[A-Za-z]+')
chapterNumberPattern = re.compile(r'\d+')
articleNumberPattern = re.compile(r'\d+(?:\.\d+)+')

partNumberPattern = re.compile(r'\d+[-–—\.\d]*(?=\.\s)')
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

rangeLabeledByWordsCheckPattern = re.compile(r'[Уу]тратил(?:[а-я]|)\s+силу')
justNumberPattern = re.compile(r'\d+')

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


def get_subheaders_from_page(page, header, hKey, sign, host,
                             subHeaderNumberPattern, baseHeader):
    subElements = page.xpath('//contents/ul/li/a')
    subHeaders = {}
    for s in subElements:
        doc_type = f"{header['doc_type']}/{sign}"
        title = s.text
        text_source_url = f"http://{host}{s.attrib['href']}"
        subHeaderNum = subHeaderNumberPattern.search(s.text)[0]
        docID = f"{hKey}/{sign}-{subHeaderNum}".upper()
        subHeaders[docID] = {
            'supertype': baseHeader['supertype'],
            'doc_type': doc_type,
            'title': title,
            'release_date': baseHeader['release_date'],
            'text_source_url': text_source_url
            }
        #break  #!!!only while debugging
    return subHeaders


def get_subheaders_ranges_frm_strs_and_clear_strs_frm_them(
        header, hKey, stringList, subhSign, subhNamePrefix,
        subhNumRangePattern, subhNumRangeNumPattern,
        subhNumRangeNumLastNum, baseHeader):
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

            for i in range(first, last+1):
                subhNum = subhNumRangeNumLastNum.sub(str(i), numTemplate)
                doc_type = f"{header['doc_type']}/{subhSign}"
                title = header['title'] + subhNamePrefix + subhNum
                text_source_url = header['text_source_url']
                docID = f"{hKey}/{subhSign}-{subhNum}".upper()
                subheaders[docID] = {
                    'supertype': baseHeader['supertype'],
                    'doc_type': doc_type,
                    'title': title,
                    'release_date': baseHeader['release_date'],
                    'text_source_url': text_source_url,
                    'text': commonText
                    }
        else:
            first = ord(subhNumRangeNumLastNum.search(rangeNums[0])[0])
            last = ord(subhNumRangeNumLastNum.search(rangeNums[1])[0])
            for i in range(first, last+1):
                subhNum = subhNumRangeNumLastNum.sub(chr(i), numTemplate)
                doc_type = f"{header['doc_type']}/{subhSign}"
                title = header['title'] + subhNamePrefix + subhNum
                text_source_url = header['text_source_url']
                docID = f"{hKey}/{subhSign}-{subhNum}".upper()
                subheaders[docID] = {
                    'supertype': baseHeader['supertype'],
                    'doc_type': doc_type,
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
        subhNumPattern, baseHeader):
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
    for i in range(len(subhListStringList)):
        doc_type = f"{header['doc_type']}/{subhSign}"
        text_source_url = header['text_source_url']
        if subhNumPattern is not None:
            subhNum = subhNumPattern.search(subhListStringList[i][0])[0]
        elif subhIndexes is None or len(subhIndexes) > 1:
            subhNum = str(i+1)
        else:
            subhNum = str(0)
        title = header['title'] + subhNamePrefix + subhNum
        docID = f"{hKey}/{subhSign}-{subhNum}".upper()
        subhText = '\n'.join(subhListStringList[i])
        subhDictStringList[docID] = subhListStringList[i]
        subheaders[docID] = {
            'supertype': baseHeader['supertype'],
            'doc_type': doc_type,
            'title': title,
            'release_date': baseHeader['release_date'],
            'text_source_url': text_source_url,
            'text': subhText
            }
    return (subheaders, subhDictStringList)


def get_subheaders_range_labeled_by_words_instead_numbers(
        allGottenHeaders, rejectingPatterns, header, hKey, stringList,
        subhSign, subhNamePrefix, subhNumPattern, baseHeader):
    if len(stringList) == 1:
        return
    indexesStrsLabeledByWords = []
    subhNums = set()
    for i in range(len(stringList)):
        if subhNumPattern.match(stringList[i]) is not None:
            subhNums.add(
                int(justNumberPattern.search(stringList[i])[0]))
            continue
        eggs = False
        for pattern in rejectingPatterns:
            if pattern.match(stringList[i]) is not None:
                eggs = True
                break
        if eggs:
            continue
        if rangeLabeledByWordsCheckPattern.search(stringList[i]) is not None:
            print(f'Warning: Article {hKey} has a range labeled by words.')
            indexesStrsLabeledByWords.append(i)
    for index in indexesStrsLabeledByWords:
        try:
            if subhNumPattern.match(stringList[index+1]) is not None:
                lastNum = int(justNumberPattern.search(stringList[index+1])[0])
                for num in range(1, lastNum):
                    subhNum = str(num)
                    docID = f"{hKey}/{subhSign}-{subhNum}".upper()
                    if (num not in subhNums and
                            docID not in allGottenHeaders):
                        commonText = stringList[index]
                        doc_type = f"{header['doc_type']}/{subhSign}"
                        title = header['title'] + subhNamePrefix + subhNum
                        text_source_url = header['text_source_url']
                        allGottenHeaders[docID] = {
                            'supertype': baseHeader['supertype'],
                            'doc_type': doc_type,
                            'title': title,
                            'release_date': baseHeader['release_date'],
                            'text_source_url': text_source_url,
                            'text': commonText
                            }
            else:
                raise Exception(f"Error: Article {hKey} has abzats after range"
                                " labeled by words.")
        except IndexError:
            raise Exception(f"Error: Article {hKey} has range labeled by "
                            "words. This range is the last abzats in the "
                            "Article, so program can't get number of "
                            "subheaders.")
    for index in indexesStrsLabeledByWords:
        del stringList[index]


def process_unique_subhs_abzats_together(
        header, hKey, stringList, subhIndexes, subhSign, subhNamePrefix,
        baseHeader):
    subheaders = {}
    if len(stringList[:subhIndexes[0]]) > 1:
        raise Exception(f"Error: Article {hKey} has multiple abzats before "
                        "subheaders.")
    abzatsDiapazonsIndexes = []
    stringToDeleteIndexes = []
    if enumerationCheckPattern.search(
                        stringList[subhIndexes[-1]]) is None:
        if subhIndexes[-1] != len(stringList)-1:
            abzatsDiapazonsIndexes.append((0, subhIndexes[-1]))
            for i in range(subhIndexes[-1]+1, len(stringList)):
                abzatsDiapazonsIndexes.append((i, i))
                stringToDeleteIndexes.append(i)
        else:
            return subheaders
    elif lastEnumElCheckPattern.search(stringList[-2]) is not None:
        raise Exception(f"Error: Article {hKey} has abzats after end of "
                        "enumeration.")
    for i in range(len(abzatsDiapazonsIndexes)):
        doc_type = f"{header['doc_type']}/{subhSign}"
        text_source_url = header['text_source_url']
        subhNum = str(i+1)
        title = header['title'] + subhNamePrefix + subhNum
        docID = f"{hKey}/{subhSign}-{subhNum}".upper()
        subhText = '\n'.join(stringList[
            abzatsDiapazonsIndexes[i][0]:abzatsDiapazonsIndexes[i][1]+1])
        subheaders[docID] = {
            'supertype': baseHeader['supertype'],
            'doc_type': doc_type,
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


def get_codex_content():
    reqHeaders = {
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

    codexMainPage, response = get_page(CODEX_URL, reqHeaders)

    supertype = doc_type = CODEX_PREFIX
    title = codexMainPage.xpath('//h1')[0].text

    releaseDateMatch = editionPattern.search(title)
    if releaseDateMatch is None:
        releaseDateMatch = relPattern.search(title)
        if releaseDateMatch is None:
            raise Exception('Cannot parse release date')
    release_date = datePattern.search(releaseDateMatch[0])[0]

    text_source_url = CODEX_URL

    codexHeaders = {}
    codexHeaders[CODEX_PREFIX] = {
        'supertype': supertype,
        'doc_type': doc_type,
        'title': title,
        'release_date': release_date,
        'text_source_url': text_source_url
        }

    baseHeader = {
        'supertype': supertype,
        'release_date': release_date,
        }

    # start of sections processing
    sectionHeaders = get_subheaders_from_page(
        codexMainPage, codexHeaders[CODEX_PREFIX], CODEX_PREFIX,
        SECTION_SIGN, HOST, sectionNumberPattern, baseHeader)
    codexHeaders.update(sectionHeaders)
    # end of sections processing

    # start of chapters processing
    chapterHeaders = {}
    for key in sectionHeaders:
        codexSectionPage, response = get_page(
            sectionHeaders[key]['text_source_url'], reqHeaders,
            response, codexHeaders[CODEX_PREFIX]['text_source_url']
            )
        chapterHeaders.update(
            get_subheaders_from_page(
                codexSectionPage, codexHeaders[CODEX_PREFIX], CODEX_PREFIX,
                CHAPTER_SIGN, HOST, chapterNumberPattern, baseHeader
                )
            )
        chaptersUpkey = dict.fromkeys(chapterHeaders.keys(), key)
    codexHeaders.update(chapterHeaders)
    # end of chapters processing

    # start of first stage of articles processing
    articleHeaders = {}
    for key in chapterHeaders:
        upkey = upperLevelKeyPattern.search(key)[0]
        codexChapterPage, response = get_page(
            chapterHeaders[key]['text_source_url'], reqHeaders,
            response, sectionHeaders[chaptersUpkey[key]]['text_source_url']
            )
        articleHeaders.update(
            get_subheaders_from_page(
                codexChapterPage, codexHeaders[CODEX_PREFIX], CODEX_PREFIX,
                ARTICLE_SIGN, HOST, articleNumberPattern, baseHeader
                )
            )
        articklesUpkey = dict.fromkeys(articleHeaders.keys(), key)
    codexHeaders.update(articleHeaders)
    # end of first stage of articles processing

    # start of last stage of articles processing
    # start of parts processing
    numArt = 1  # debug
    for key in articleHeaders:
        print(f'Processing article {numArt}/{len(articleHeaders)}...',
              end='\r')  # debug
        numArt += 1  # debug
        upkey = upperLevelKeyPattern.search(key)[0]
        #testURL = 'http://www.consultant.ru/document/cons_doc_LAW_34661/ec55ca680f2de0bc822beeaf4dcbbe162b81059d/'
        #articleHeaders[key]['text_source_url'] = testURL
        codexArticlePage, response = get_page(
            articleHeaders[key]['text_source_url'], reqHeaders,
            response, chapterHeaders[articklesUpkey[key]]['text_source_url']
            )
        try:
            textTitle = codexArticlePage.xpath(
                '//div[@class="text"]/h1/div[@style]/span')[0].text_content()
        except IndexError:
            textTitle = codexArticlePage.xpath('//h1')[0].text_content()
        codexHeaders[key]['title'] = textTitle
        stringList = []
        spans = codexArticlePage.xpath('//div[@class="text"]/div[@style]/span')
        for string in spans:
            string_text = string.text_content()
            if string_text != '\xa0':
                stringList.append(string_text)
        articleText = textTitle + '\n\n' + '\n'.join(stringList)
        codexHeaders[key]['text'] = articleText
        # end of article processing

        # start of notes processing
        noteStrings = []
        for i in range(len(stringList)):
            if notePattern.match(stringList[i]) is not None:
                noteStrings = stringList[i:]
                del stringList[i:]
                break
        # In the future, it will be necessary
        # to expand the processing of notes.
        if noteStrings:
            noteHeaders = get_subheaders_from_strings_by_indexes(
                articleHeaders[key], key, noteStrings, [0], NOTE_SIGN,
                NOTE_NAME_PREFIX, None, baseHeader
                )[0]
            codexHeaders.update(noteHeaders)
        # end of notes processing

        codexHeaders.update(
            get_subheaders_ranges_frm_strs_and_clear_strs_frm_them(
                articleHeaders[key], key, stringList, PART_SIGN,
                PART_NAME_PREFIX, partNumberRangePattern,
                partNumberRangeNumPattern, partNumberRangeNumLastNum,
                baseHeader
                )
            )

        get_subheaders_range_labeled_by_words_instead_numbers(
            codexHeaders, [punktNumberPattern, punktNumberRangePattern,
                           podpunktNumberPattern, podpunktNumberRangePattern],
            articleHeaders[key], key, stringList, PART_SIGN,
            PART_NAME_PREFIX,  partNumberPattern, baseHeader
            )

        partsIndexes = get_subheaders_indexes(stringList, partNumberPattern)
        if not partsIndexes:
            if (len(stringList) > 1 and
                    enumerationCheckPattern.search(stringList[0]) is None):
                raise Exception(f"Error: Article {key} is divided into abzats "
                                "but not into parts.")
            else:
                continue

        partHeaders, partsDictStringList = \
            get_subheaders_from_strings_by_indexes(
                articleHeaders[key], key, stringList, partsIndexes, PART_SIGN,
                PART_NAME_PREFIX, partNumberPattern, baseHeader
                )
        codexHeaders.update(partHeaders)

        # start of punkts processing
        for key in partHeaders:
            codexHeaders.update(
                get_subheaders_ranges_frm_strs_and_clear_strs_frm_them(
                    partHeaders[key], key, partsDictStringList[key],
                    PUNKT_SIGN, PUNKT_NAME_PREFIX, punktNumberRangePattern,
                    punktNumberRangeNumPattern, punktNumberRangeNumLastNum,
                    baseHeader
                    )
                )

            get_subheaders_range_labeled_by_words_instead_numbers(
                codexHeaders, [podpunktNumberPattern,
                               podpunktNumberRangePattern,
                               partNumberPattern],
                partHeaders[key], key, partsDictStringList[key], PUNKT_SIGN,
                PUNKT_NAME_PREFIX,  punktNumberPattern, baseHeader
            )

            punktIndexes = get_subheaders_indexes(partsDictStringList[key],
                                                  punktNumberPattern)

            # just need to check on big dataset
            if (len(partsDictStringList[key]) > 2 and
                    endsWithDashCheckPattern.search(
                        partsDictStringList[key][0]) is not None):
                print(f"Warning: Part {key} has multiple abzats after '-', "
                      "please check.")

            if not punktIndexes:
                if (len(partsDictStringList[key]) > 1 and
                        endsWithDashCheckPattern.search(
                            partsDictStringList[key][0]) is None):
                    abzatsHeaders = get_subheaders_from_strings_by_indexes(
                        partHeaders[key], key, partsDictStringList[key], None,
                        ABZATS_SIGN, ABZATS_NAME_PREFIX, None, baseHeader
                        )[0]
                    codexHeaders.update(abzatsHeaders)
                else:
                    continue
            else:
                codexHeaders.update(
                    process_unique_subhs_abzats_together(
                        partHeaders[key], key, partsDictStringList[key],
                        punktIndexes, ABZATS_SIGN, ABZATS_NAME_PREFIX,
                        baseHeader
                        )
                    )

                punktHeaders, punktsDictStringList = \
                    get_subheaders_from_strings_by_indexes(
                        partHeaders[key], key, partsDictStringList[key],
                        punktIndexes, PUNKT_SIGN, PUNKT_NAME_PREFIX,
                        punktNumberPattern, baseHeader
                        )
                codexHeaders.update(punktHeaders)

                # start of podpunkts processing
                for key in punktHeaders:
                    codexHeaders.update(
                        get_subheaders_ranges_frm_strs_and_clear_strs_frm_them(
                            punktHeaders[key], key, punktsDictStringList[key],
                            PODPUNKT_SIGN, PODPUNKT_NAME_PREFIX,
                            podpunktNumberRangePattern,
                            podpunktNumberRangeNumPattern,
                            podpunktNumberRangeNumLastNum, baseHeader
                            )
                        )
                    podpunktIndexes = get_subheaders_indexes(
                        punktsDictStringList[key], podpunktNumberPattern)

                    # just need to check on big dataset
                    if (len(punktsDictStringList[key]) > 2 and
                            endsWithDashCheckPattern.search(
                                punktsDictStringList[key][0]) is not None):
                        print(f"Warning: Punkt {key} has multiple abzats after"
                              " '-', please check.")

                    if not podpunktIndexes:
                        if len(punktsDictStringList[key]) > 1 and \
                                endsWithDashCheckPattern.search(
                                    punktsDictStringList[key][0]) is None:
                            abzatsHeaders = \
                                get_subheaders_from_strings_by_indexes(
                                    punktHeaders[key], key,
                                    punktsDictStringList[key], None,
                                    ABZATS_SIGN, ABZATS_NAME_PREFIX,
                                    None, baseHeader
                                    )[0]
                            codexHeaders.update(abzatsHeaders)
                        else:
                            continue
                    else:
                        codexHeaders.update(
                            process_unique_subhs_abzats_together(
                                punktHeaders[key], key,
                                punktsDictStringList[key], podpunktIndexes,
                                ABZATS_SIGN, ABZATS_NAME_PREFIX, baseHeader
                                )
                            )

                        podpunktHeaders, podpunktsDictStringList = \
                            get_subheaders_from_strings_by_indexes(
                                punktHeaders[key], key,
                                punktsDictStringList[key], podpunktIndexes,
                                PODPUNKT_SIGN, PODPUNKT_NAME_PREFIX,
                                podpunktNumberPattern, baseHeader
                                )
                        codexHeaders.update(podpunktHeaders)
                        for key in podpunktHeaders:
                            if len(podpunktsDictStringList[key]) > 1 and \
                                endsWithDashCheckPattern.search(
                                    podpunktsDictStringList[key][0]) is None:
                                abzatsHeaders = \
                                    get_subheaders_from_strings_by_indexes(
                                        podpunktHeaders[key], key,
                                        podpunktsDictStringList[key], None,
                                        ABZATS_SIGN, ABZATS_NAME_PREFIX,
                                        None, baseHeader
                                        )[0]
                                codexHeaders.update(abzatsHeaders)
                            else:
                                continue
                # end of podpunkts processing
        # end of punkts processing
    # end of last stage of articles processing
    # end of parts processing
# end of codex processing
    return codexHeaders

if __name__ == '__main__':
    import os
    import json
    import time
    start_time = time.time()
    codexHeaders = get_codex_content()
    print(f"Codex processing spent {time.time()-start_time} seconds.\n"
          f"Total IDs: {len(codexHeaders)}.")
    pathToFile = f'{CODEX_PREFIX}_codexHeaders.json'
    dirname = os.path.dirname(pathToFile)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(pathToFile, 'w', encoding='utf-8') as jsonFile:
        json.dump(codexHeaders, jsonFile)
    input("press any key...")
