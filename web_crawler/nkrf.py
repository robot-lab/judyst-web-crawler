if __package__:
    from web_crawler.rf_legal_acts_processing_functions import *
else:
    from rf_legal_acts_processing_functions import *

CODEX_URLS = (
    'http://www.consultant.ru/document/cons_doc_LAW_19671',
    'http://www.consultant.ru/document/cons_doc_LAW_28165')
CODEX_PREFIX = 'НКРФ'
CODEX_PART_SIGN = 'Ч'

PART_SIGN = PUNKT_SIGN
PART_NAME_PREFIX = PUNKT_NAME_PREFIX
PUNKT_SIGN = PODPUNKT_SIGN
PUNKT_NAME_PREFIX = PODPUNKT_NAME_PREFIX


def get_codex_content():
    reqHeaders = REQHEADERS
    codexHeaders = {}
    for i in range(len(CODEX_URLS)):
        # debug print
        print(f"\n{CODEX_PREFIX} {CODEX_PART_SIGN} {i+1}/{len(CODEX_URLS)}:")
        CODEX_URL = CODEX_URLS[i]
        codexMainPage, response = get_page(CODEX_URL, reqHeaders)
        supertype = CODEX_PREFIX
        doc_type = f"{CODEX_PREFIX}/{CODEX_PART_SIGN}"
        title = codexMainPage.xpath('//h1')[0].text

        # getting page with title
        spam1 = {'doc_type': CODEX_PREFIX}
        spam2 = {
            'supertype': '',
            'release_date': '',
            }
        spam3 = get_subheaders_from_page(
            codexMainPage, spam1, CODEX_PREFIX,
            SECTION_SIGN, HOST, sectionNumberPattern, spam2, CODEX_PREFIX)

        # getting true codex part title:
        pageWithTitle, spam = get_page(
            list(spam3.values())[0]['text_source_url'], reqHeaders)
        title = pageWithTitle.xpath('//b[@id="documentTitleLink"]')[0].text

        releaseDateMatch = editionPattern.search(title)
        if releaseDateMatch is None:
            releaseDateMatch = relPattern.search(title)
            if releaseDateMatch is None:
                raise Exception('Cannot parse release date')
        release_date = datePattern.search(releaseDateMatch[0])[0]

        text_source_url = CODEX_URL

        CODEX_PART_KEY = f"{CODEX_PREFIX}/{CODEX_PART_SIGN}-{str(i+1)}"
        codexHeaders[CODEX_PART_KEY] = {
            'supertype': supertype,
            'doc_type': doc_type,
            'absolute_path': CODEX_PART_KEY,
            'title': title,
            'release_date': release_date,
            'text_source_url': text_source_url
            }

        baseHeader = {
            'supertype': supertype,
            'release_date': release_date,
            }

        # start of sections processing
        headerWithCodexDocType = {'doc_type': CODEX_PREFIX}
        sectionHeaders = get_subheaders_from_page(
            codexMainPage, headerWithCodexDocType, CODEX_PREFIX,
            SECTION_SIGN, HOST, sectionNumberPattern, baseHeader,
            codexHeaders[CODEX_PART_KEY]['absolute_path'])
        codexHeaders.update(sectionHeaders)
        # end of sections processing

        # start of chapters processing
        chapterHeaders = {}
        for key in sectionHeaders:
            codexSectionPage, response = get_page(
                sectionHeaders[key]['text_source_url'], reqHeaders,
                response, codexHeaders[CODEX_PART_KEY]['text_source_url']
                )
            temp = get_subheaders_from_page(
                    codexSectionPage, headerWithCodexDocType, CODEX_PREFIX,
                    CHAPTER_SIGN, HOST, chapterNumberPattern, baseHeader,
                    sectionHeaders[key]['absolute_path']
                    )
            chapterHeaders.update(temp)
        codexHeaders.update(chapterHeaders)
        # end of chapters processing

        # start of first stage of articles processing
        articleHeaders = {}
        for key in chapterHeaders:
            codexChapterPage, response = get_page(
                chapterHeaders[key]['text_source_url'], reqHeaders,
                response, codexHeaders[CODEX_PART_KEY]['text_source_url']
                )
            ahs = get_subheaders_from_page(
                    codexChapterPage, headerWithCodexDocType, CODEX_PREFIX,
                    ARTICLE_SIGN, HOST, articlesNumbersPattern, baseHeader,
                    chapterHeaders[key]['absolute_path'], onlyFirst=False
                    )
            if ahs:
                articleHeaders.update(ahs)
            else:
                print(f"Warning: Chapter {key} is no more valid.")
                ahs = get_subheaders_from_header_title(
                    chapterHeaders[key]['title'],
                    chapterHeaders[key]['text_source_url'],
                    headerWithCodexDocType, CODEX_PREFIX,
                    ARTICLE_SIGN, articlesStartPattern,
                    articlesNumbersPattern, baseHeader,
                    chapterHeaders[key]['absolute_path']
                )
                if ahs:
                    articleHeaders.update(ahs)
                else:
                    raise Exception(f"Cannot get articles from chapter {key}")
        codexHeaders.update(articleHeaders)
        # end of first stage of articles processing

        # start of last stage of articles processing
        # start of parts processing
        numArt = 1  # debug
        for key in articleHeaders:
            print(f'Processing article {numArt}/{len(articleHeaders)}...',
                  end='\r')  # debug
            numArt += 1  # debug
            # testURL = 'testUrl'
            # articleHeaders[key]['text_source_url'] = testURL
            codexArticlePage, response = get_page(
                articleHeaders[key]['text_source_url'], reqHeaders,
                response,
                codexHeaders[CODEX_PART_KEY]['text_source_url']
                )
            try:
                textTitle = codexArticlePage.xpath(
                    '//div[@class="text"]/h1/div[@style]/span')[0].\
                        text_content()
            except IndexError:
                textTitle = codexArticlePage.xpath('//h1')[0].text_content()
            codexHeaders[key]['title'] = textTitle
            stringList = []
            spans = codexArticlePage.xpath(
                '//div[@class="text"]/div[@style]/span')
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
                    NOTE_NAME_PREFIX, None, baseHeader,
                    articleHeaders[key]['absolute_path']
                    )[0]
                codexHeaders.update(noteHeaders)
            # end of notes processing

            codexHeaders.update(
                get_subhdrs_rngs_frm_strs_and_clear_strs_frm_them(
                    articleHeaders[key], key, stringList, PART_SIGN,
                    PART_NAME_PREFIX, partNumberRangePattern,
                    partNumberRangeNumPattern, partNumberRangeNumLastNum,
                    baseHeader, articleHeaders[key]['absolute_path']
                    )
                )

            get_subheaders_range_labeled_by_words_instead_numbers(
                codexHeaders, [punktNumberPattern, punktNumberRangePattern,
                               podpunktNumberPattern,
                               podpunktNumberRangePattern,
                               loneNoMoreValidAbzatsPattern],
                articleHeaders[key], key, stringList, PART_SIGN,
                PART_NAME_PREFIX,  partNumberPattern, baseHeader,
                articleHeaders[key]['absolute_path'], True
                )

            partsIndexes = get_subheaders_indexes(stringList,
                                                  partNumberPattern)
            if not partsIndexes:
                if (len(stringList) > 1 and
                        lastEnumElCheckPattern.search(
                            stringList[0]) is not None):
                    abzatsHeaders = get_subheaders_from_strings_by_indexes(
                            articleHeaders[key], key, stringList, None,
                            ABZATS_SIGN, ABZATS_NAME_PREFIX, None, baseHeader,
                            articleHeaders[key]['absolute_path']
                            )[0]
                    codexHeaders.update(abzatsHeaders)
                    continue
                else:
                    continue

            partHeaders, partsDictStringList = \
                get_subheaders_from_strings_by_indexes(
                    articleHeaders[key], key, stringList, partsIndexes,
                    PART_SIGN, PART_NAME_PREFIX, partNumberPattern, baseHeader,
                    articleHeaders[key]['absolute_path']
                    )
            codexHeaders.update(partHeaders)

            # start of punkts processing
            for key in partHeaders:
                codexHeaders.update(
                    get_subhdrs_rngs_frm_strs_and_clear_strs_frm_them(
                        partHeaders[key], key, partsDictStringList[key],
                        PUNKT_SIGN, PUNKT_NAME_PREFIX, punktNumberRangePattern,
                        punktNumberRangeNumPattern, punktNumberRangeNumLastNum,
                        baseHeader, partHeaders[key]['absolute_path']
                        )
                    )

                get_subheaders_range_labeled_by_words_instead_numbers(
                    codexHeaders, [podpunktNumberPattern,
                                   podpunktNumberRangePattern,
                                   partNumberPattern,
                                   loneNoMoreValidAbzatsPattern],
                    partHeaders[key], key, partsDictStringList[key],
                    PUNKT_SIGN, PUNKT_NAME_PREFIX, punktNumberPattern,
                    baseHeader, partHeaders[key]['absolute_path']
                    )

                punktIndexes = get_subheaders_indexes(partsDictStringList[key],
                                                      punktNumberPattern)

                # just need to check on big dataset
                if (len(partsDictStringList[key]) > 2 and
                        endsWithDashCheckPattern.search(
                            partsDictStringList[key][0]) is not None):
                    print(f"Warning: Part {key} has multiple abzats after '-',"
                          " please check.")

                if not punktIndexes:
                    if (len(partsDictStringList[key]) > 1 and
                            endsWithDashCheckPattern.search(
                                partsDictStringList[key][0]) is None):
                        abzatsHeaders = get_subheaders_from_strings_by_indexes(
                            partHeaders[key], key, partsDictStringList[key],
                            None, ABZATS_SIGN, ABZATS_NAME_PREFIX, None,
                            baseHeader, partHeaders[key]['absolute_path']
                            )[0]
                        codexHeaders.update(abzatsHeaders)
                    else:
                        continue
                else:
                    codexHeaders.update(
                        process_unique_subhs_abzats_together(
                            partHeaders[key], key, partsDictStringList[key],
                            punktIndexes, ABZATS_SIGN, ABZATS_NAME_PREFIX,
                            baseHeader, partHeaders[key]['absolute_path']
                            )
                        )

                    punktHeaders, punktsDictStringList = \
                        get_subheaders_from_strings_by_indexes(
                            partHeaders[key], key, partsDictStringList[key],
                            punktIndexes, PUNKT_SIGN, PUNKT_NAME_PREFIX,
                            punktNumberPattern, baseHeader,
                            partHeaders[key]['absolute_path']
                            )
                    codexHeaders.update(punktHeaders)

                    # avos'
                    # start of podpunkts processing
                    for key in punktHeaders:
                        codexHeaders.update(
                            get_subhdrs_rngs_frm_strs_and_clear_strs_frm_them(
                                punktHeaders[key], key,
                                punktsDictStringList[key],
                                ABZATS_SIGN, ABZATS_NAME_PREFIX,
                                podpunktNumberRangePattern,
                                podpunktNumberRangeNumPattern,
                                podpunktNumberRangeNumLastNum, baseHeader,
                                punktHeaders[key]['absolute_path']
                                )
                            )
                        podpunktIndexes = get_subheaders_indexes(
                            punktsDictStringList[key], podpunktNumberPattern)

                        # just need to check on big dataset
                        if (len(punktsDictStringList[key]) > 2 and
                                endsWithDashCheckPattern.search(
                                    punktsDictStringList[key][0]) is not None):
                            print(f"Warning: Punkt {key} has multiple abzats "
                                  "after '-', please check.")

                        if not podpunktIndexes:
                            if len(punktsDictStringList[key]) > 1 and \
                                    endsWithDashCheckPattern.search(
                                        punktsDictStringList[key][0]) is None:
                                abzatsHeaders = \
                                    get_subheaders_from_strings_by_indexes(
                                        punktHeaders[key], key,
                                        punktsDictStringList[key], None,
                                        ABZATS_SIGN, ABZATS_NAME_PREFIX,
                                        None, baseHeader,
                                        punktHeaders[key]['absolute_path']
                                        )[0]
                                codexHeaders.update(abzatsHeaders)
                            else:
                                continue
                        else:
                            codexHeaders.update(
                                process_unique_subhs_abzats_together(
                                    punktHeaders[key], key,
                                    punktsDictStringList[key], podpunktIndexes,
                                    ABZATS_SIGN, ABZATS_NAME_PREFIX, baseHeader,
                                    punktHeaders[key]['absolute_path']
                                    )
                                )

                            podpunktHeaders, podpunktsDictStringList = \
                                get_subheaders_from_strings_by_indexes(
                                    punktHeaders[key], key,
                                    punktsDictStringList[key], podpunktIndexes,
                                    ABZATS_SIGN, ABZATS_NAME_PREFIX,
                                    podpunktNumberPattern, baseHeader,
                                    punktHeaders[key]['absolute_path']
                                    )
                            codexHeaders.update(podpunktHeaders)
                            for key in podpunktHeaders:
                                if len(podpunktsDictStringList[key]) > 1 and \
                                    endsWithDashCheckPattern.search(
                                        podpunktsDictStringList[key][0]) \
                                        is None:
                                    abzatsHeaders = \
                                        get_subheaders_from_strings_by_indexes(
                                            podpunktHeaders[key], key,
                                            podpunktsDictStringList[key], None,
                                            ABZATS_SIGN, ABZATS_NAME_PREFIX,
                                            None, baseHeader,
                                            podpunktHeaders[key]['absolute_path']
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
    print(f"\nCodex processing spent {time.time()-start_time} seconds.\n"
          f"Total IDs: {len(codexHeaders)}.")
    pathToFile = f'{CODEX_PREFIX}_codexHeaders.json'
    dirname = os.path.dirname(pathToFile)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(pathToFile, 'w', encoding='utf-8') as jsonFile:
        json.dump(codexHeaders, jsonFile)
    input("press any key...")
    # pathToFile = '2НКРФ_codexHeaders.json'
    # with open(pathToFile, 'rt', encoding='utf-8') as jsonFile:
    #     jsonOLD = json.load(jsonFile)
    # pathToFile1 = '3НКРФ_codexHeaders.json'
    # with open(pathToFile1, 'rt', encoding='utf-8') as jsonFile1:
    #     jsonNEW = json.load(jsonFile1)
    # oldkeys = jsonOLD.keys()
    # newkeys = jsonNEW.keys()
    # ab = oldkeys - newkeys
    # ba = newkeys - oldkeys
    # print(1)
