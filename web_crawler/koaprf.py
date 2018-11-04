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

notePattern = re.compile(r'Примечани[ея][\.:]')

upperLevelKeyPattern = re.compile(r'.*(?=/)')
sectionNumberPattern = re.compile(r'[A-Za-z]+')
chapterNumberPattern = re.compile(r'\d+')
articleNumberPattern = re.compile(r'\d+(?:\.\d+)+')

partNumberPattern = re.compile(r'\d+[-\.\d]*(?=\.\s)')
partNumberRangePattern = re.compile(r'\d+[-\.\d]*\s+-\s+\d+[-\.\d]*(?=\s)')
partNumberRangeNumPattern = re.compile(r'\d+[-\.\d]*(?=\s)')
partNumberRangeNumLastNum = re.compile(r'(?:\d+$|\d+(?=\.$))')

punktNumberPattern = re.compile(r'\d+[-\.\d]*(?=\)\s)')
punktNumberRangePattern = re.compile(
    r'\d+[-\.\d]*\)\s*?-\s*?\d+[-\.\d]*\)(?=\s)')
punktNumberRangeNumPattern = re.compile(
    r'(?:\d+[-\.\d]*(?=\)\s)|\d+[-\.\d]*(?=\)-))')
punktNumberRangeNumLastNum = partNumberRangeNumLastNum

podpunktNumberPattern = re.compile(r'[а-яa-z][-.а-яa-z]*(?=\)\s)')
podpunktNumberRangePattern = re.compile(
    r'[а-яa-z][-.а-яa-z]*\)\s*?-\s*?[а-яa-z][-.а-яa-z]*\)(?=\s)')
podpunktNumberRangeNumPattern = re.compile(
    r'(?:[а-яa-z][-.а-яa-z]*(?=\)\s)|[а-яa-z][-.а-яa-z]*(?=\)-))')
podpunktNumberRangeNumLastNum = re.compile(r'[а-яa-z]+$')


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

    # start of articles processing
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

    # start of parts processing
    numArt = 1  #debug
    for key in articleHeaders:
        print(f'Processing article {numArt}/{len(articleHeaders)}...', end='\r')  #debug
        numArt += 1  #debug
        upkey = upperLevelKeyPattern.search(key)[0]
        #testURL = 'http://www.consultant.ru/document/cons_doc_LAW_34661/050f7cdf016b07506efdb7120d14daefc7c5d74d/'
        #testURL = 'http://www.consultant.ru/document/cons_doc_LAW_34661/c4e643d138637f4eafb763d628fc44ef99c71a15/'
        #testURL = 'http://www.consultant.ru/document/cons_doc_LAW_34661/9bb3917d25392ccbd6a8b265099b3c86333cdac3/'
        #testURL = 'http://www.consultant.ru/document/cons_doc_LAW_34661/be2c7e5355fd620186edb2c60b566fabdb2fdce8/'
        #testURL = 'http://www.consultant.ru/document/cons_doc_LAW_34661/095cf3d72883289f916eab42a9925e29ddb731a7/'
        #testURL = 'http://www.consultant.ru/document/cons_doc_LAW_34661/8132296f390c25aa030ef52774e6a1ed039040bb/'
        #testURL = 'http://www.consultant.ru/document/cons_doc_LAW_34661/f6f8eaf735bbe508bc35e770ada89f5b4263cebc/'
        #testURL = 'http://www.consultant.ru/document/cons_doc_LAW_34661/c1bcab16c81eba5a2d9cafa87dd4a3abae6c0790/'
        #testURL = 'http://www.consultant.ru/document/cons_doc_LAW_34661/8132296f390c25aa030ef52774e6a1ed039040bb/'
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
        # end of articles processing

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

        partsIndexes = get_subheaders_indexes(stringList, partNumberPattern)
        if not partsIndexes:
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
            punktIndexes = get_subheaders_indexes(partsDictStringList[key],
                                                  punktNumberPattern)
            if not punktIndexes:
                if (len(partsDictStringList[key]) > 1 and
                        not partsDictStringList[key][0].endswith('-')):
                    abzatsHeaders = get_subheaders_from_strings_by_indexes(
                        partHeaders[key], key, partsDictStringList[key], None,
                        ABZATS_SIGN, ABZATS_NAME_PREFIX, None, baseHeader
                        )[0]
                    codexHeaders.update(abzatsHeaders)
                else:
                    continue
            else:
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
                    if not podpunktIndexes:
                        if len(punktsDictStringList[key]) > 1 and \
                                not punktsDictStringList[key][0].endswith('-'):
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
                                not podpunktsDictStringList[key][0]. \
                                    endswith('-'):
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
