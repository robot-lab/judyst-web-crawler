import re
import random
import zipfile

# Import libs:

import urllib.request
# License: MIT License

import lxml.html
# License: BSD license; Installing: python -m pip install lxml

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
    'Accept-Charset': 'utf-8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }

_CODE_PART_SIGN = 'ЧК'
_REDACTIONS_SIGN = 'РЕД'
_SECTION_SIGN = 'Р'
_SUBSECTION_SIGN = 'ПДР'
_CHAPTER_SIGN = 'ГЛ'
_PARAGRAPH_SIGN = 'ПРГ'
_SUBPARAGRAPH_SIGN = 'ПДПРГ'
_ARTICLE_SIGN = 'СТ'
_NOTE_SIGN = 'ПРМ'
_PART_SIGN = 'Ч'
_ABZATS_SIGN = 'А'
_PUNKT_SIGN = 'П'
_PODPUNKT_SIGN = 'ПП'

_NOTE_NAME_PREFIX = 'Примечание'
_PART_NAME_PREFIX = 'Часть '
_PUNKT_NAME_PREFIX = 'Пункт '
_PODPUNKT_NAME_PREFIX = 'Подпункт '
_ABZATS_NAME_PREFIX = 'Абзац '

_sectionNumberPattern = re.compile(
    r'(?<=(?i)Раздел\s)\s*?[A-Za-z]+(?:\.[-–—\d]+)*')
_subsectionNumberPattern = re.compile(
    r'(?<=(?i)Подраздел\s)\s*?\d+(?:\.[-–—\d]+)*(?=\.)')
_paragraphNumberPattern = re.compile(r'(?<=§\s)\s*?\d+(?:\.[-–—\d]+)*(?=\.)')
_subparagraphNumberPattern = re.compile(r'(?<=^)\d+(?:\.[-–—\d]+)*(?=\.)')
_chapterNumberPattern = re.compile(
    r'(?<=(?i)Глава\s)\s*?\d+(?:\.[-–—\d]+)*(?=\.)')
_articleNumberPattern = re.compile(
    r'(?<=(?i)Статья\s)\s*?\d+(?:\.[-–—\d]+)*(?=\.)')
_articlesNumbersPattern = re.compile(
    r'(?:(?<=[Сс]татья\s)\s*?\d+(?:\.[-–—\d]+)*(?=\.$)|'
    r'(?<=[Сс]татья\s)\s*?\d+(?:\.[-–—\d]+)*(?=\.\s)|'
    r'(?<=[Сс]татья\s)\s*?\d+(?:\.[-–—\d]+)*(?=\s)|'
    r'(?<=[Сс]татья\s)\s*?\d+(?:\.[-–—\d]+)*(?=\,)|'
    r'(?<=[Сс]татья\s)\s*?\d+(?:\.[-–—\d]+)*(?=\)))'
    )

_partNumberPattern = re.compile(r'\d+(?:\.[-–—\d]+)*(?=\.)')
_partNumberRangePattern = re.compile(
   r'\d+(?:\.[-–—\d]+\.*?)*\s*?[-–—]\s*?\d+(?:\.[-–—\d]+\.*?)*(?=\.)')
_partNumberRangeNumPattern = re.compile(r'\d+(?:\.[-–—\d]+)*')
_partNumberRangeNumLastNum = re.compile(r'(?:\d+$|\d+(?=\.$))')

_punktNumberPattern = re.compile(r'\d+(?:\.[-–—\d]+)*(?=\)\s)')
_punktNumberRangePattern = re.compile(
    r'\d+(?:\.[-–—\d]+)*\)\s*?-\s*?\d+(?:\.[-–—\d]+)*\)(?=\s)')

_podpunktNumberPattern = re.compile(r'[а-яa-z][-–—.а-яa-z]*(?=\)\s)')
_podpunktNumberRangePattern = re.compile(
    r'[а-яa-z][-.а-яa-z]*\)\s*?-\s*?[а-яa-z][-–—.а-яa-z]*\)(?=\s)')

_noteCheckPattern = re.compile(
    r'(?:Примечание.(?!\s[Уу]тратило силу\.)|'
    r'Примечания(?:\.|:))(?!\s[Уу]тратили силу\.)')
_noteWordDelPattern = re.compile(
    r'(?:Примечание.\s+|Примечания:\s+|Примечания.\s+)')
_partNumberDelPattern = re.compile(r'\d+(?:\.[-–—\d]+)*\.\s*')
_redactionBlockPattern = re.compile(
    rf'(?:(?<=/){_REDACTIONS_SIGN}-[-N\.\d]*?(?=/)|'
    rf'(?<=/){_REDACTIONS_SIGN}-[-N\.\d]*)')


_justNumberPattern = re.compile(r'\d+')
_justWordPattern = re.compile(r'[а-яА-яёЁ]+')

_datePattern = re.compile(r'\d\d\.\d\d\.\d{4}')
_monthDict = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12'
}

_strDatePattern = re.compile(r'.*?(?=\sгода)')
_comparRdNumPattern1 = re.compile(r'(?<=&diff=)\d+')
_compareRdNumPattern2 = re.compile(r'(?<=&n=)\d+')

_parHtmlPattern = re.compile(r'(?:\<div[\w\W]*?(?=\<a id="Par)|\<div.*div\>)')
_parLabelInSavedHtmlPattern = re.compile(r'(?<=#Par)\d+(?=")')
_titleInSaveHtmContentsPattern = re.compile(
    r'(?:(?<=>◦).*?(?=<)|(?<=>)(?:[А-Яа-яEё§\d]|&sect;|&quot;).*?(?=<))')
_savedHtmContentsPattern = re.compile(r'\<div[\w\W]*?\<table')
_parInStrInSavedHtmPattern = re.compile(r'(?<=id="Par)\d+(?=")')
_emptyLinePattern = re.compile(
    r'<div class="(?:\w+\s+){2}\w+"(?:\s*?style=".*?")*?></div>')
_notArticleLineStart = '<div class="s2B aC bH'
_articleLineStart = '<div class="s2B aJ bH'
_strsForDel1Start = '<table border'
_strsForDel2Start = '<tr style'
_consNoteStart = '<td class="bD'
_redactionNoteCheckPattern = re.compile(
    r'<div class="(?:\w+\s+){2}\w+"(?:\s*?style=".*?")*?>\(')
_articleTextStart = '<div class="s0 aJ bG'


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


def _decode_json_from_str(content):
    try:
        structure = json.loads(content, encoding='utf-8')
    except UnicodeDecodeError:
        content = content.decode('windows-1251').encode('utf-8')
        structure = json.loads(content, encoding='utf-8')
    return structure


class _BaseCode:
    CODE_URLS = (
        'http://www.consultant.ru/document/Кодекс_часть1/',
        'http://www.consultant.ru/document/Кодекс_часть2/',
        'http://www.consultant.ru/document/Кодекс_часть3/',
        )
    CODE_PREFIX = 'Аббревиатура кодекса'
    CODE_PART_NAMES = ('Кодекс Ч1', 'Кодекс Ч2', 'Кодекс Ч3')
    CODE_PART_SIGN = _CODE_PART_SIGN

    REDACTIONS_SIGN = _REDACTIONS_SIGN
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

    sectionNumberPattern = _sectionNumberPattern
    subsectionNumberPattern = _subsectionNumberPattern
    paragraphNumberPattern = _paragraphNumberPattern
    subparagraphNumberPattern = _subparagraphNumberPattern
    chapterNumberPattern = _chapterNumberPattern
    articleNumberPattern = _articleNumberPattern

    articlesNumbersPattern = _articlesNumbersPattern

    partNumberPattern = _partNumberPattern
    partNumberRangePattern = _partNumberRangePattern
    partNumberRangeNumPattern = _partNumberRangeNumPattern
    partNumberRangeNumLastNum = _partNumberRangeNumLastNum

    punktNumberPattern = _punktNumberPattern
    punktNumberRangePattern = _punktNumberRangePattern

    podpunktNumberPattern = _podpunktNumberPattern
    podpunktNumberRangePattern = _podpunktNumberRangePattern

    noteCheckPattern = _noteCheckPattern
    noteWordDelPattern = _noteWordDelPattern
    partNumberDelPattern = _partNumberDelPattern
    redactionBlockPattern = re.compile(
        rf'(?:(?<=/){REDACTIONS_SIGN}-[-N\.\d]*?(?=/)|'
        rf'(?<=/){REDACTIONS_SIGN}-[-N\.\d]*)')

    @classmethod
    def get_document_redactions(cls, url, reqHeaders, prevResponse=None,
                                referer=None):
        page, response = _get_page(url, reqHeaders, prevResponse, referer)
        lastRedNum = page.xpath('//q[@id="fullTextLink"]')[0].attrib['nd']
        reqRedUrl = (f"http://{_HOST}/cons/cgi/online.cgi?req=doc&base=LAW"
                     f"&n={lastRedNum}&content=editions")
        content, response = _get_page(reqRedUrl, reqHeaders, response, url,
                                      raw=True)
        jsonRedactions = _decode_json_from_str(content)
        return jsonRedactions['editions']['list'], response

    @classmethod
    def create_header(cls, CUR_RD_KEY, supertype, doc_type, absolute_path,
                      title, release_date, effective_date, attached, dstLabel,
                      parLabelInSavedHtm, rdNote=None, consNote=None,
                      text=None):
        attached.append(cls.CUR_CODE_PART_NAME)
        t = cls.codeHeaders[CUR_RD_KEY]
        ts = t['cons_selected_info']
        il = (f"http://{_HOST}/cons/cgi/online.cgi?req=query"
              f"&REFDOC={ts['rd_doc_number']}&REFBASE=LAW&REFPAGE=0"
              f"&REFTYPE=CDLT_CHILDLESS_CONTENTS_ITEM_MAIN_BACKREFS"
              f"&mode=backrefs&REFDST={dstLabel}")
        header = {
            'supertype': supertype,
            'doc_type': doc_type,
            'absolute_path': absolute_path,
            'title': title,
            'release_date': release_date,
            'effective_date': effective_date,
            'text_source_url':
                f"{t['text']['filename']}#Par{parLabelInSavedHtm}",
            'cons_selected_info': {
                'rd_doc_number': ts['rd_doc_number'],
                'rd_doc_link': f"{ts['rd_doc_link']}&dst={dstLabel}",
                'intext_label': dstLabel,
                'redaction_comparison_link':
                    f"{ts['redaction_comparison_link']}&dst={dstLabel}",
                'addit_info_link': il,
                'attached_titles': attached
                }
            }
        if text is not None:
            header['text'] = text
        if rdNote is not None:
            header['cons_selected_info']['redaction_note'] = rdNote
        if consNote is not None:
            header['cons_selected_info']['cons_note'] = consNote
        return header

    @classmethod
    def create_subheader(cls, hKey, SUBH_SIGN, absolute_path, title,
                         rdNote=None, consNote=None, text=None):
        t = cls.codeHeaders[hKey]
        ts = t['cons_selected_info']
        attached = ts['attached_titles'][:]
        attached.insert(0, title)
        header = {
            'supertype': t['supertype'],
            'doc_type': f"{cls.codeHeaders[hKey]['doc_type']}/{SUBH_SIGN}",
            'absolute_path': absolute_path,
            'title': title,
            'release_date': t['release_date'],
            'effective_date': t['effective_date'],
            'text_source_url': t['text_source_url'],
            'cons_selected_info': {
                'rd_doc_number': ts['rd_doc_number'],
                'rd_doc_link': ts['rd_doc_link'],
                'intext_label': ts['intext_label'],
                'redaction_comparison_link':
                    ts['redaction_comparison_link'],
                'attached_titles': attached
                }
            }
        if text is not None:
            header['text'] = text
        if rdNote is not None:
            header['cons_selected_info']['redaction_note'] = rdNote
        if consNote is not None:
            header['cons_selected_info']['cons_note'] = consNote
        return header

    @classmethod
    def get_subhdrs_frm_tree_and_return_lines_for_articles(
            cls, treeItem, hKey, CUR_RD_KEY, rekeyedAttachedTitles,
            splittedHtm):
        def frequent_case(SIGN, numPattern, item):
            nonlocal hKey
            nonlocal supertype
            nonlocal doc_type
            nonlocal absolute_path
            nonlocal title
            nonlocal release_date
            nonlocal effective_date
            nonlocal attached
            nonlocal dstLabel
            nonlocal htmParNum
            nonlocal rekeyedAttachedTitles
            nonlocal CUR_RD_KEY
            nonlocal articleLines
            nonlocal rd_doc_id_prefix
            nonlocal splittedHtm
            num = numPattern.search(item['caption'])
            if num is not None:
                commonPart = f"{SIGN}-{num[0].lstrip()}"
                if (numPattern == cls.sectionNumberPattern or
                        numPattern == cls.chapterNumberPattern):
                    doc_id = f"{rd_doc_id_prefix}/{commonPart}"
                else:
                    doc_id = f"{hKey}/{commonPart}"
                doc_type = f"{cls.CODE_PREFIX}/{SIGN}"
                absolute_path = \
                    f"{cls.codeHeaders[hKey]['absolute_path']}/{commonPart}"
                cls.codeHeaders[doc_id] = cls.create_header(
                    CUR_RD_KEY, supertype, doc_type, absolute_path, title,
                    release_date, effective_date, attached, dstLabel,
                    htmParNum, rdNote, consNote)
                # debug print
                cls.recursCounter += 1
                print(f"Recursive processing of headers up to and including "
                      f"articles {cls.recursCounter}...", end='\r')
                if splittedHtm[title]['type'] == cls.ARTICLE_SIGN:
                    articleLines[doc_id] = splittedHtm[title]['lines']
                if item['treeItem']:
                    articleLines.update(
                        cls.get_subhdrs_frm_tree_and_return_lines_for_articles(
                            item['treeItem'], doc_id, CUR_RD_KEY,
                            rekeyedAttachedTitles, splittedHtm
                            )
                        )
                else:
                    return 'tree is null'
            else:
                return 'parsed is null'

        articleLines = {}
        supertype = cls.CODE_PREFIX
        rd_doc_id_prefix = \
            (f"{cls.CODE_PREFIX}/"
             f"{cls.redactionBlockPattern.search(CUR_RD_KEY)[0]}")
        release_date = cls.codeHeaders[CUR_RD_KEY]['release_date']
        effective_date = cls.codeHeaders[CUR_RD_KEY]['effective_date']

        cls.partOfCodeCounter = 1
        for item in treeItem:
            if 'caption' not in item:
                commonPart = f"{cls.CODE_PART_SIGN}-{cls.partOfCodeCounter}"
                doc_id = f"{rd_doc_id_prefix}/{commonPart}"
                absolute_path = \
                    f"{cls.codeHeaders[hKey]['absolute_path']}/{commonPart}"
                doc_type = f"{cls.CODE_PREFIX}/{cls.CODE_PART_SIGN}"
                title = item['_text']
                dstLabel = item['label']
                try:
                    attached = rekeyedAttachedTitles[title]['tooltip']
                except KeyError:
                    continue
                htmParNum = splittedHtm[title]['htmParNum']
                if 'cons_note' in splittedHtm[title]:
                    consNote = splittedHtm[title]['cons_note']
                else:
                    consNote = None
                if 'redaction_note' in splittedHtm[title]:
                    rdNote = splittedHtm[title]['redaction_note']
                else:
                    rdNote = None
                cls.codeHeaders[doc_id] = cls.create_header(
                    CUR_RD_KEY, supertype, doc_type, absolute_path, title,
                    release_date, effective_date, attached, dstLabel,
                    htmParNum, rdNote, consNote)
                # debug print
                cls.recursCounter += 1
                print(f"Recursive processing of headers up to and including "
                      f"articles {cls.recursCounter}...", end='\r')
                if item['treeItem']:
                    articleLines.update(
                        cls.get_subhdrs_frm_tree_and_return_lines_for_articles(
                            item['treeItem'], doc_id, CUR_RD_KEY,
                            rekeyedAttachedTitles, splittedHtm
                            )
                        )
                else:
                    return articleLines
                continue

            title = item['caption'] + item['_text']
            dstLabel = item['label']
            attached = rekeyedAttachedTitles[title]['tooltip']
            htmParNum = splittedHtm[title]['htmParNum']
            if 'cons_note' in splittedHtm[title]:
                    consNote = splittedHtm[title]['cons_note']
            else:
                consNote = None
            if 'redaction_note' in splittedHtm[title]:
                rdNote = splittedHtm[title]['redaction_note']
            else:
                rdNote = None

            spam = frequent_case(cls.SECTION_SIGN, cls.sectionNumberPattern,
                                 item)
            if spam == 'tree is null':
                return articleLines
            elif spam != 'parsed is null':
                continue
            spam = frequent_case(cls.SUBSECTION_SIGN,
                                 cls.subsectionNumberPattern, item)
            if spam == 'tree is null':
                return articleLines
            elif spam != 'parsed is null':
                continue
            spam = frequent_case(cls.CHAPTER_SIGN, cls.chapterNumberPattern,
                                 item)
            if spam == 'tree is null':
                return articleLines
            elif spam != 'parsed is null':
                continue
            spam = frequent_case(cls.PARAGRAPH_SIGN,
                                 cls.paragraphNumberPattern, item)
            if spam == 'tree is null':
                return articleLines
            elif spam != 'parsed is null':
                continue
            spam = frequent_case(cls.SUBPARAGRAPH_SIGN,
                                 cls.subparagraphNumberPattern, item)
            if spam == 'tree is null':
                return articleLines
            elif spam != 'parsed is null':
                continue
            nums = cls.articlesNumbersPattern.findall(item['caption'])
            if not nums:
                rangeNums = cls.partNumberRangePattern.search(item['caption'])
                if rangeNums is None:
                    rangeNums = cls.partNumberRangePattern.search(
                        item['caption']+item['_text'])
                if rangeNums is not None:
                    rNums = cls.partNumberRangeNumPattern.findall(rangeNums[0])
                    template = rNums[0]
                    digitFrom = int(
                        cls.partNumberRangeNumLastNum.search(rNums[0])[0])
                    digitTo = int(
                        cls.partNumberRangeNumLastNum.search(rNums[1])[0])
                for i in range(digitFrom, digitTo+1):
                    num = cls.partNumberRangeNumLastNum.sub(str(i), template)
                    nums.append(num)
            if nums:
                for num in nums:
                    commonPart = f"{cls.ARTICLE_SIGN}-{num.lstrip()}"
                    doc_id = f"{rd_doc_id_prefix}/{commonPart}"
                    absolute_path = \
                        (f"{cls.codeHeaders[hKey]['absolute_path']}/"
                         f"{commonPart}")
                    doc_type = f"{cls.CODE_PREFIX}/{cls.ARTICLE_SIGN}"
                    cls.codeHeaders[doc_id] = cls.create_header(
                        CUR_RD_KEY, supertype, doc_type, absolute_path, title,
                        release_date, effective_date, attached, dstLabel,
                        htmParNum, rdNote, consNote)
                    # debug print
                    cls.recursCounter += 1
                    print(
                        f"Recursive processing of headers up to and including "
                        f"articles {cls.recursCounter}...", end='\r')
                    if item['treeItem']:
                        raise Exception(f"Article cannot have an treeItem.")
                    else:
                        articleLines[doc_id] = splittedHtm[title]['lines']
            else:
                raise Exception(f"{hKey}. Cannot parse a number.")
        return articleLines

    @classmethod
    def get_par_html(cls, allHtml: str, par: int):  # not used anymore
        parStartPattern = re.compile(f'<a id="Par{par}"')
        startPos = parStartPattern.search(allHtml).start(0)
        parHtml = _parHtmlPattern.search(allHtml, pos=startPos)
        if parHtml is not None:
            return lxml.html.document_fromstring(parHtml[0])
        else:
            raise Exception("Cannot find par in html.")

    @classmethod
    def get_paras_and_titles_from_saved_htm(cls, savedHtm):
        savedHtmContents = _savedHtmContentsPattern.search(savedHtm)[0]
        lines = savedHtmContents.splitlines()
        result = {}
        for line in lines:
            match = _parLabelInSavedHtmlPattern.search(line)
            if match is not None:
                par = match[0]
                title = _titleInSaveHtmContentsPattern.search(line)
                result[par] = title[0]
        return result

    @classmethod
    def split_saved_htm(cls, savedHtm):
        lines = savedHtm.splitlines()
        result = {}
        start = end = continueSearch = nextSearchStart = 0
        rotten = True
        egg = False
        parasTitles = cls.get_paras_and_titles_from_saved_htm(savedHtm)
        while egg is not rotten:
            for i in range(nextSearchStart, len(lines)):
                if _emptyLinePattern.match(lines[i]) is not None:
                    start = i + 1
                    continue
                if lines[i].startswith(_notArticleLineStart):
                    materialType = 'not ' + cls.ARTICLE_SIGN
                elif lines[i].startswith(_articleLineStart):
                    materialType = cls.ARTICLE_SIGN
                else:
                    continue
                match = _parInStrInSavedHtmPattern.search(lines[i])
                if match is None:
                    continue
                htmParNum = match[0]
                title = parasTitles[htmParNum].\
                    replace('&sect;', '§').\
                    replace('&quot;', '"')
                for z in range(i+1, len(lines)):
                    if _emptyLinePattern.match(lines[z]) is not None:
                        continueSearch = z
                        break
                break
            for j in range(continueSearch, len(lines)):
                if _emptyLinePattern.match(lines[j]) is not None:
                    end = j
                    continue
                if (lines[j].startswith(_notArticleLineStart) or
                        lines[j].startswith(_articleLineStart) or
                        j == len(lines)-1):
                    nextSearchStart = end
                    if j == len(lines)-1:
                        egg = True
                    else:
                        break
            result[title] = {
                'htmParNum': htmParNum,
                'type': materialType,
                'lines': lines[start:end]
            }
        return result

    @classmethod
    def get_cons_note_from_str(cls, string):
        consNote = lxml.html.document_fromstring(string)
        xpathRes = consNote.xpath('//div')
        xl = []
        for x in xpathRes:
            xl.append(x.text_content().strip())
        return '\n'.join(xl)

    @classmethod
    def clear_splitted_htm_and_get_plus_add_cons_notes(cls, splittedHtm):
        for key in splittedHtm:
            lines = splittedHtm[key]['lines']
            notes = []
            rdNote = ''
            indexesForDeleting = []
            for i in range(len(lines)):
                if (lines[i].startswith(_articleTextStart) and
                        _redactionNoteCheckPattern.match(lines[i]) is None):
                    break
                elif _emptyLinePattern.match(lines[i]) is not None:
                    indexesForDeleting.append(i)
                    if (lines[i+1].startswith(_strsForDel1Start) and
                            _emptyLinePattern.match(lines[i+4]) is not None):
                        continue
                    else:
                        break
                elif (lines[i].startswith(_strsForDel1Start) or
                        lines[i].startswith(_strsForDel2Start)):
                    indexesForDeleting.append(i)
                elif _redactionNoteCheckPattern.match(lines[i]) is not None:
                    rdNote = lxml.html.document_fromstring(
                                                    lines[i]).text_content()
                    indexesForDeleting.append(i)
                elif lines[i].startswith(_consNoteStart):
                    indexesForDeleting.append(i)
                    consNote = cls.get_cons_note_from_str(lines[i])
                    notes.append(consNote)
            if notes:
                splittedHtm[key]['cons_note'] = '\n\n'.join(notes)
            if rdNote:
                splittedHtm[key]['redaction_note'] = rdNote
            correction = 0
            for index in indexesForDeleting:
                del lines[index-correction]
                correction += 1

    @classmethod
    def build_article_subheaders_treeItem(cls, articleLines, CUR_RD_KEY):
        print('')
        cleanedArticleLines = {}
        for key in articleLines:
            cleanedArticleLines[key] = []
            for line in articleLines[key]:
                if (line.startswith(_consNoteStart) or
                        line.startswith(_articleTextStart)):
                    cleanedArticleLines[key].append(line)
                # There are white spaces around images with formulas.
                # elif _emptyLinePattern.match(line) is not None:
                #     print(f"Warning: article {key} has empty line in lines "
                #           f"(maybe mr. president's sign)")
                #     break

        articleLinesWithNotes = {}
        for key in cleanedArticleLines:
            articleLinesWithNotes[key] = []
            lines = cleanedArticleLines[key]
            for i in range(len(lines)):
                tempDict = {}
                if (lines[i].startswith(_articleTextStart) and
                        _redactionNoteCheckPattern.match(lines[i]) is None):
                    text = lxml.html.document_fromstring(
                                                    lines[i]).text_content()
                    tempDict['text'] = text
                    try:
                        if lines[i-1].startswith(_consNoteStart):
                            tempDict['cons_note'] = \
                                cls.get_cons_note_from_str(lines[i-1])
                    except IndexError:
                        pass
                    try:
                        match = _redactionNoteCheckPattern.match(lines[i+1])
                        if match is not None:
                            rdNote = lxml.html.document_fromstring(
                                                    lines[i+1]).text_content()
                            tempDict['redaction_note'] = rdNote
                    except IndexError:
                        pass
                    articleLinesWithNotes[key].append(tempDict)

        # work in progress
        treeItem = {}
        aC = 0
        for key in articleLinesWithNotes:
            aC += 1
            print(f"Article processing (divide into parts) "
                  f"{aC}/{len(articleLinesWithNotes)}...", end='\r')
            if not len(articleLinesWithNotes[key]) > 1:
                continue
            indexes = []
            lines = articleLinesWithNotes[key]
            for i in range(len(lines)):
                if (cls.partNumberPattern.match(
                        lines[i]['text']) is not None and
                    cls.partNumberRangePattern.match(
                        lines[i]['text']) is None):
                    indexes.append(i)
                if cls.noteCheckPattern.match(lines[i]['text']) is not None:
                    doc_id = f"{key}/{cls.NOTE_SIGN}"
                    absolute_path = (f"{cls.codeHeaders[key]['absolute_path']}"
                                     f"/{cls.NOTE_SIGN}")
                    title = cls.NOTE_NAME_PREFIX
                    if 'redaction_note' in lines[i]:
                        rdNote = lines[i]['redaction_note']
                    else:
                        rdNote = None
                    if 'cons_note' in lines[i]:
                        consNote = lines[i]['cons_note']
                    else:
                        consNote = None
                    textLines = []
                    for line in lines[i:]:
                        textLines.append(line['text'])
                    text = '\n'.join(textLines)
                    cls.codeHeaders[doc_id] = cls.create_subheader(
                        key, cls.NOTE_SIGN, absolute_path, title, rdNote,
                        consNote, text)
                    if i != len(lines)-1:
                        lines[i]['text'] = cls.noteWordDelPattern.sub(
                                                        '', lines[i]['text'])
                        if lines[i]['text']:
                            treeItem[doc_id] = lines[i:]
                        else:
                            treeItem[doc_id] = lines[i+1:]
                    del lines[i:]
                    break
            if indexes:
                for j in range(len(indexes)):
                    i = indexes[j]
                    num = cls.partNumberPattern.match(lines[i]['text'])[0]
                    doc_id = f"{key}/{cls.PART_SIGN}-{num}"
                    absolute_path = (f"{cls.codeHeaders[key]['absolute_path']}"
                                     f"/{cls.PART_SIGN}-{num}")
                    title = cls.PART_NAME_PREFIX + str(num)
                    if 'redaction_note' in lines[i]:
                        rdNote = lines[i]['redaction_note']
                    else:
                        rdNote = None
                    if 'cons_note' in lines[i]:
                        consNote = lines[i]['cons_note']
                    else:
                        consNote = None
                    try:
                        i2 = indexes[j+1]
                    except IndexError:
                        i2 = len(lines)
                    textLines = []
                    for line in lines[i:i2]:
                        textLines.append(line['text'])
                    text = '\n'.join(textLines)
                    cls.codeHeaders[doc_id] = cls.create_subheader(
                        key, cls.PART_SIGN, absolute_path, title, rdNote,
                        consNote, text)
                    if i2-i != 1:
                        pass  # work in progress (abzats, punkts, podpunkts)
                        # lines[i]['text'] = cls.partNumberDelPattern.sub(
                        #   '', lines[i]['text'])
                        # treeItem[doc_id] = lines[i:i2]
            else:
                pass
                # work in progress (abzats, punkts, podpunkts)
        # return treeItem
        return None

    @classmethod
    def get_code_content(
            cls, pathToResultJsonLinesFile,
            pathToFileForKeysThathWereDownloadedYet):
        cls.codeHeaders = {}
        for i in range(len(cls.CODE_URLS)):
            # i = 1 #debug
            if len(cls.CODE_URLS) > 1:
                # debug print
                print(f"\n\n\n---{cls.CODE_PREFIX} {cls.CODE_PART_SIGN} "
                      f"{i+1}/{len(cls.CODE_URLS)}:", end='')
                code_doc_type = f"{cls.CODE_PREFIX}/ЧАСТЬ"
                cls.CODE_PART_KEY = \
                    f"{cls.CODE_PREFIX}_{cls.CODE_PART_SIGN}-{str(i+1)}"
            else:
                # debug print
                print(f"\n\n\n---{cls.CODE_PREFIX}:", end='')
                code_doc_type = f"{cls.CODE_PREFIX}/ВЕСЬ"
                cls.CODE_PART_KEY = cls.CODE_PREFIX
            cls.CUR_CODE_PART_NAME = cls.CODE_PART_NAMES[i]
            supertype = cls.CODE_PREFIX
            text_source_url = codeURL = cls.CODE_URLS[i]
            # debug start
            # testurl = 'http://www.consultant.ru/document/cons_doc_law_10699/'
            # testurl = 'http://www.consultant.ru/document/cons_doc_LAW_5142/'
            # codeURL = testurl
            # debug end
            pageWithTitleAndDocNum, response = _get_page(codeURL,
                                                         _REQHEADERS)
            titleElements = pageWithTitleAndDocNum.xpath(
                '//div[@class="h2"]/div[@class="HC"]/span')
            titleStrings = []
            for el in titleElements:
                if el.text is not None:
                    titleStrings.append(el.text)
            title = '. '.join(titleStrings)
            strWithDate = pageWithTitleAndDocNum.xpath(
                '//meta[@name="description"]')[0].attrib["content"]
            strDate = _strDatePattern.match(strWithDate)[0]
            dayYear = _justNumberPattern.findall(strDate)
            monthWord = _justWordPattern.search(strDate)[0]
            release_date = f"{dayYear[0]}.{_monthDict[monthWord]}.{dayYear[1]}"

            redactions, response = cls.get_document_redactions(codeURL,
                                                               _REQHEADERS)
            cls.codeHeaders[cls.CODE_PART_KEY] = {
                'supertype': supertype,
                'doc_type': code_doc_type,
                'absolute_path': cls.CODE_PART_KEY,
                'title': title,
                'release_date': release_date,
                'text_source_url': text_source_url,
                'cons_selected_info': {'redactions': redactions}
                }
            rj = 0  # debug
            try:
                with open(pathToFileForKeysThathWereDownloadedYet, 'r',
                          encoding='utf-8') as jsonlinesFile:
                    yetProcessed = jsonlinesFile.read().splitlines()
            except FileNotFoundError:
                yetProcessed = []
            for red in redactions:
                # debug print
                rj += 1
                print(f"\n\n--{cls.REDACTIONS_SIGN} {red['edDate']} "
                      f"{rj}/{len(redactions)}:")
                doc_type = f"{code_doc_type}/{cls.REDACTIONS_SIGN}"
                release_date = red['edDate']
                match = _datePattern.search(red['reddate'])
                if match is not None:
                    effective_date = match[0]
                else:
                    effective_date = 'не действовала'
                rdDocNumber = red['nd']
                absolute_path = doc_id = \
                    (f"{cls.CODE_PART_KEY}/{cls.REDACTIONS_SIGN}-"
                     f"N{red['number']}-{effective_date}")
                if doc_id in yetProcessed:
                    continue
                url = (f"http://{_HOST}/cons/cgi/online.cgi?req=doc"
                       f"&base=LAW&n={rdDocNumber}&content=text")
                prevUrl = url
                docContent, response = _get_page(
                    url, _REQHEADERS, response, prevUrl, raw=True)
                docContent = _decode_json_from_str(docContent)

                url = (
                    f"http://{_HOST}/cons/cgi/online.cgi?req=doc"
                    f"&n={rdDocNumber}&base=LAW&content=contents&op=attached")
                attachedTitles, response = _get_page(
                    url, _REQHEADERS, response, prevUrl, raw=True)
                attachedTitles = _decode_json_from_str(
                    attachedTitles)['contents']['attachedTitles']

                url = (f"http://{_HOST}/cons/cgi/online.cgi?req=doc"
                       f"&n={rdDocNumber}&base=LAW&content=contents")
                treeItem, response = _get_page(
                    url, _REQHEADERS, response, prevUrl, raw=True)
                treeItem = _decode_json_from_str(
                    treeItem)['contents']['treeItem']

                text_source_url = \
                    (f"http://{_HOST}/cons/cgi/online.cgi?req=doc"
                     f"&base=LAW&n={rdDocNumber}")

                page, response = _get_page(
                    text_source_url, _REQHEADERS, response, prevUrl)
                spam = page.xpath("//script")
                title = None
                for s in spam:
                    try:
                        spamDict = _decode_json_from_str(s.attrib["settings"])
                    except ValueError:
                        continue
                    if 'title' in spamDict:
                        title = spamDict['title']
                        break
                if title is None:
                    raise Exception(f"Doc {doc_id}. Cannot parse title.")

                htmFileName = doc_id.replace('/', '_')
                url = \
                    (f"http://{_HOST}/cons/cgi/online.cgi?req=export"
                     f"&type=html&base=LAW&n={rdDocNumber}")
                rar, response = _get_page(
                    url, _REQHEADERS, response, prevUrl, raw=True)
                with open(f'{htmFileName}.zip', 'wb') as rarFile:
                    rarFile.write(rar)
                with zipfile.ZipFile(f'{htmFileName}.zip') as file:
                    files = file.namelist()
                    if files[0].endswith('.htm'):
                        filename = files[0]
                    else:
                        filename = files[1]
                    file.extract(filename, '')
                os.remove(f'{htmFileName}.zip')
                with open(filename, 'r', encoding='utf-8') as htmFile:
                    savedHtmText = htmFile.read()
                os.remove(filename)
                text = {
                    'filename': f'{htmFileName}.htm',
                    'content': savedHtmText
                }
                consInTextLabel = treeItem[0]['label']
                inHtmLabel = '0'  # stab

                if red['type'] == 'n':
                    compareRdDocNum = _comparRdNumPattern1.search(
                        docContent['settings']['compareEditions']['href'])[0]
                    redactionComparisonLink = (
                        f"http://{_HOST}/cons/cgi/online.cgi?req=doc"
                        f"&base=LAW&div=LAW&n={rdDocNumber}"
                        f"&diff={compareRdDocNum}")
                else:
                    compareRdDocNum = _compareRdNumPattern2.search(
                        docContent['settings']['compareEditions']['href'])[0]
                    redactionComparisonLink = (
                            f"http://{_HOST}/cons/cgi/online.cgi?req=doc"
                            f"&base=LAW&div=LAW&n={compareRdDocNum}"
                            f"&diff={rdDocNumber}")

                cls.codeHeaders[doc_id] = {
                    'supertype': supertype,
                    'doc_type': doc_type,
                    'absolute_path': absolute_path,
                    'title': title,
                    'release_date': release_date,
                    'effective_date': effective_date,
                    'text': text,
                    'text_source_url': f"{text['filename']}#Par{inHtmLabel}",
                    'cons_selected_info': {
                        'rd_doc_number': rdDocNumber,
                        'reference_info': docContent['esse']['content'],
                        'rd_number': red['number'],
                        'rd_type': red['type'],
                        'rd_description': red['_text'],
                        'rd_doc_link': text_source_url,
                        'intext_label': consInTextLabel,
                        'unicode_text_link': (
                            f"http://{_HOST}/cons/cgi/online.cgi?req=export"
                            f"&type=utxt&base=LAW&n={rdDocNumber}"),
                        'prev_rd_doc_num': compareRdDocNum,
                        'changes_review_link': (
                            f"http://{_HOST}/cons/cgi/online.cgi?req=query"
                            f"&REFDOC={rdDocNumber}&REFBASE=LAW&mode=chgreview"
                            f"&content=instant"),
                        'redaction_comparison_link': redactionComparisonLink,
                        'addit_info_link': (
                            f"http://{_HOST}/cons/cgi/online.cgi?req=query"
                            f"&div=LAW&REFDOC={rdDocNumber}&REFBASE=LAW"
                            f"&REFTYPE=CDLT_DOC_I_BACKREFS&mode=backrefs")
                        }  # ,
                    # 'cons_raw_info': {
                    #     'docContent': docContent,
                    #     'attachedTitles': attachedTitles,
                    #     'treeItem': treeItem
                    #     }
                    }
                rekeyedAttachedTitles = {}
                del attachedTitles[0]
                for at in attachedTitles:
                    rekeyedAttachedTitles[at['tooltip'][0]] = at

                splittedHtm = cls.split_saved_htm(savedHtmText)
                cls.clear_splitted_htm_and_get_plus_add_cons_notes(splittedHtm)

                cls.recursCounter = 0
                CUR_RD_KEY = doc_id
                articleLines = \
                    cls.get_subhdrs_frm_tree_and_return_lines_for_articles(
                        treeItem, doc_id, CUR_RD_KEY, rekeyedAttachedTitles,
                        splittedHtm)

                articleSubheadersTreeItem = \
                    cls.build_article_subheaders_treeItem(articleLines,
                                                          CUR_RD_KEY)
                with open(pathToResultJsonLinesFile, 'at',
                          encoding='utf-8') as jsonlinesFile:
                    for key in cls.codeHeaders:
                        jsonlinesFile.write(json.dumps(
                            {key: cls.codeHeaders[key]}) + '\n')
                cls.codeHeaders = {}
                with open(pathToFileForKeysThathWereDownloadedYet, 'at',
                          encoding='utf-8') as file:
                    file.write(doc_id + '\n')
                # print('ok')
            # pathToFile = f'{cls.CODE_PART_KEY}.json'
            # with open(pathToFile, 'wt', encoding='utf-8') as jsonFile:
            #     json.dump(cls.codeHeaders, jsonFile)
            #     cls.codeHeaders = {}
        return cls.codeHeaders


class _Ukrf(_BaseCode):
    CODE_URLS = (
        'http://www.consultant.ru/document/cons_doc_LAW_10699/',)
    CODE_PREFIX = 'УКРФ'
    CODE_PART_NAMES = ('УК РФ',)


class _Koaprf(_BaseCode):
    CODE_URLS = (
        'http://www.consultant.ru/document/cons_doc_LAW_34661',)
    CODE_PREFIX = 'КОАПРФ'
    CODE_PART_NAMES = ('КоАП РФ',)


class _Nkrf (_BaseCode):
    CODE_URLS = (
        'http://www.consultant.ru/document/cons_doc_LAW_19671',
        'http://www.consultant.ru/document/cons_doc_LAW_28165')
    CODE_PREFIX = 'НКРФ'
    CODE_PART_NAMES = ('НК РФ Общая часть',
                       'НК РФ Специальная (особенная) часть')

    PART_NAME_PREFIX = 'Часть (пункт) '
    PUNKT_NAME_PREFIX = 'Пункт (подпункт) '
    PODPUNKT_NAME_PREFIX = 'Подпункт (подподпункт) '


class _Gkrf(_BaseCode):
    CODE_URLS = (
        'http://www.consultant.ru/document/cons_doc_LAW_5142/',
        'http://www.consultant.ru/document/cons_doc_LAW_9027/',
        'http://www.consultant.ru/document/cons_doc_LAW_34154/',
        'http://www.consultant.ru/document/cons_doc_LAW_64629/'
        )
    CODE_PREFIX = 'ГКРФ'
    CODE_PART_NAMES = ('ГК РФ Часть 1', 'ГК РФ Часть 2', 'ГК РФ Часть 3',
                       'ГК РФ Часть 4')

    PART_NAME_PREFIX = 'Часть (пункт) '
    PUNKT_NAME_PREFIX = 'Пункт (подпункт) '
    PODPUNKT_NAME_PREFIX = 'Подпункт (подподпункт) '


_codesParsers = {
    'КОАПРФ': _Koaprf,
    'НКРФ': _Nkrf,
    'ГКРФ': _Gkrf,
    'УКРФ': _Ukrf
}

_ALL_CODES = frozenset(_codesParsers.keys())


def get_content(
        codes: set=_ALL_CODES,
        pathToResultJsonLinesFile='codeHeaders.jsonlines',
        pathToFileForKeysThathWereDownloadedYet='processedYet.jsonlines'):
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
        codeContent = _codesParsers[code].get_code_content(
            pathToResultJsonLinesFile, pathToFileForKeysThathWereDownloadedYet)
        codesContent.update(codeContent)
    return codesContent


if __name__ == '__main__':
    import os
    import json
    import time
    start_time = time.time()
    # codes = {'КОАПРФ', 'НКРФ', 'ГКРФ', 'УКРФ'}
    # codes = {'КОАПРФ'}
    # codes = {'УКРФ'}
    # codes = 'КОАПРФ'
    # codes = {'НКРФ'}
    # codes = {'ГКРФ'}
    codes = {'ГКРФ', 'НКРФ'}
    codeHeaders = get_content(codes)
    print(f"\nCodes processing spent {time.time()-start_time} seconds.\n")
    # pathToFile = f'{list(codes)[0]}_codeHeaders.json'
    # dirname = os.path.dirname(pathToFile)
    # if dirname:
    #     os.makedirs(dirname, exist_ok=True)
    # with open(pathToFile, 'w', encoding='utf-8') as jsonFile:
    #     json.dump(codeHeaders, jsonFile)
    input("press any key...")
    # pathToFile = 'code1.json'
    # with open(pathToFile, 'rt', encoding='utf-8') as jsonFile:
    #     jsonOLD = json.load(jsonFile)
    # pathToFile1 = 'code2.json'
    # with open(pathToFile1, 'rt', encoding='utf-8') as jsonFile1:
    #     jsonNEW = json.load(jsonFile1)
    # oldkeys = jsonOLD.keys()
    # newkeys = jsonNEW.keys()
    # ab = oldkeys - newkeys
    # ba = newkeys - oldkeys
    # print(1)
