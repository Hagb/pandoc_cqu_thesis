from . import texcommands
import panflute as pf
import sys
import os
from xml.sax.saxutils import quoteattr
import locale
from datetime import date

inline_const_commands = {
    r'newLine':
    pf.LineBreak(),
    r'tabL':
    pf.RawInline(
        '<w:r><w:ptab w:relativeTo="margin" w:alignment="left" w:leader="none"/></w:r>',
        format="openxml"),
    r'tabR':
    pf.RawInline(
        '<w:r><w:ptab w:relativeTo="margin" w:alignment="right" w:leader="none"/></w:r>',
        format="openxml"),
    r'tabC':
    pf.RawInline(
        '<w:r><w:ptab w:relativeTo="margin" w:alignment="center" w:leader="none"/></w:r>',
        format="openxml"),
    r'tab':
    pf.RawInline("<w:r><w:tab/></w:r>", format="openxml"),
}

block_const_commands = {
    r'newPage':
    pf.RawBlock("<w:p><w:r><w:br w:type=\"page\" /></w:r></w:p>",
                format="openxml"),
    r'Reference': pf.Div(identifier='refs'),
}


def tocRaw(title='', format=r'TOC \o "1-3" \h \z \u', docinfo=None):
    TOC = pf.RawBlock(
        r'<w:sdt><w:sdtPr><w:docPartObj><w:docPartGallery w:val="Table of Contents"/><w:docPartUnique/></w:docPartObj></w:sdtPr><w:sdtContent><w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/><w:instrText xml:space="preserve">'
        + format
        + r'</w:instrText><w:fldChar w:fldCharType="separate"/><w:fldChar w:fldCharType="end"/></w:r></w:p></w:sdtContent></w:sdt>', format="openxml")
    return [
        pf.Div(pf.Para(pf.Span(pf.Str(title), identifier="TOC")),
               attributes={"custom-style": "TOC Heading"}),
        TOC
    ] if title else TOC


def newSectionRaw(paramStr="", docinfo=None):
    return pf.RawBlock('<w:p><w:pPr><w:sectPr>' + paramStr +
                       '</w:sectPr></w:pPr></w:p>', format='openxml')


def includeDoc(path, docinfo=None):
    current_path = docinfo[2].workPath or os.path.abspath('.')
    if ':' not in path:
        path = current_path + '/' + path
    path = quoteattr(path.replace('\\', '\\\\'))
    return pf.Div(pf.Para(
        pf.RawInline(
            '<w:pPr><w:ind w:firstLineChars="0" w:firstLine="0"/></w:pPr>'
            '<w:r><w:fldChar w:fldCharType="begin"/><w:instrText xml:space="preserve">'
            f'IncludeText {path}</w:instrText><w:fldChar w:fldCharType="end"/></w:r>', format="openxml"),
    ), attributes={'custom-style': 'noindent'})


def metadataBlock(name, docinfo):
    data = docinfo[1].metadata[name]
    if isinstance(data, pf.MetaBlocks):
        return list(data.content)
    else:
        return pf.Para(*data.content)


def get_date(meta):
    if hasattr(meta, 'date'):
        return date.fromisoformat(meta.date)
    else:
        date_strs = list(map(int, meta.date.split('-')))
        if len(date_strs) == 2:
            date_strs.append(1)
        date_ = date(year=date_strs[0], month=date_strs[1], day=date_strs[2])
        pf.debug(date_)
        setattr(meta, 'date_', date_)
        return date_


def ccoverdate(arg, docinfo):
    date_ = get_date(docinfo[2])
    return pf.Str(f'{date_.year}年{date_.month}月')


def ecoverdate(arg, docinfo):
    lc_time_backup = locale.getlocale(locale.LC_TIME)
    locale.setlocale(locale.LC_TIME, (None, None))
    date_ = get_date(docinfo[2])
    elem = pf.Str(date_.strftime('%B %Y'))
    locale.setlocale(locale.LC_TIME, lc_time_backup)
    return elem


def keywords(title, sep, keywords_meta):
    content = [pf.Span(pf.Str(title), attributes={'custom-style': 'Key Word'})]
    for n, i in enumerate(keywords_meta):
        if n:
            content.append(pf.Str(sep))
        content.extend(i.content)
    return content


null_para = pf.Para(pf.Span())


inline_function_commands = {
    'Space': lambda x, docinfo=None: [pf.Space()] * (1 if x == "" else int(x)),
    'KeyWord': lambda x, docinfo=None: pf.Span(pf.Str(x), attributes={'custom-style': 'Key Word'}),
    'refs': lambda x, docinfo=None: pf.RawInline(f'<w:fldSimple w:instr=" REF {x} \\h "/>', format="openxml"),
    'Style': lambda x, docinfo=None: pf.RawInline(f'''<w:pPr><w:pStyle w:val="{x}"/></w:pPr>''', format='openxml'),
    'metadata': lambda name, docinfo: list(docinfo[1].metadata[name].content),
    'metadataStr': lambda name, docinfo: pf.Str(str(docinfo[1].get_metadata(name))),
    'cdate': ccoverdate,
    'edate': ecoverdate,
    'ckeywords': lambda x, docinfo: keywords('关键词：', '，', docinfo[1].metadata['keywords']),
    'ekeywords': lambda x, docinfo: keywords('Keywords: ', ', ', docinfo[1].metadata['keywords-en'])
}

block_function_commands = {
    'newPara': lambda x="1", docinfo=None: [null_para] * (1 if x == "" else int(x)),
    'tocRaw': tocRaw,
    'newSectionRaw': newSectionRaw,
    'includeDoc': includeDoc,
    'metadata': metadataBlock
}


def main(doc=None, meta=None):
    replacer = texcommands.ConstTexCommandReplace(
        inline_const_commands, inline_function_commands, block_const_commands, block_function_commands)
    return pf.run_filter(replacer.action, prepare=replacer.prepare, doc=doc)


if __name__ == '__main__':
    sys.exit(main())
