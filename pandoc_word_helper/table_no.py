import panflute as pf
from .meta import Meta
import re
top_level = Meta.chaptersDepth if Meta.chapters else ''
tableSeqName = Meta.tableTitle # 题注前缀的文字和SEQ的内容相同，以便于在Word中产生相同的前缀

section_no = pf.RawInline(
    f'''<w:fldSimple w:instr=" STYLEREF {top_level} \s"/>''', format="openxml")
table_no = pf.RawInline(
    f'''<w:fldSimple w:instr=" SEQ {tableSeqName} \* ARABIC \s {top_level}"/>''',
    format="openxml")
table_no2 = pf.RawInline(
    f'''<w:fldSimple w:instr=" SEQ {tableSeqName} \c \* ARABIC \s {top_level} "/>''',
    format="openxml")
    # 重复上一个编号


class TableCaptionReplace():
    math_no = 1
    anchor_re = re.compile(r'{#([^}]+)}')

    def action(self, elem, doc):
        if isinstance(elem, pf.Table):
            elem: pf.Table
            # pf.debug("Table!")
            # 表格下面结构是Table.Caption [Plain]
            # table.caption.content[0].content才会得到Plain中的各个元素

            # 表格的题注内容长度为0，则表格题注无内容
            # 若表格无题注，则直接返回表格，不做处理
            if len(elem.caption.content) == 0:
                return elem

            if '-' in elem.caption.classes or 'unnumbered' in elem.caption.classes:
                new_caption = []
            else:
                new_caption = [
                    # 题注前缀
                    pf.Str(Meta.tableTitle),
                    pf.Span(section_no if Meta.chapters else pf.Span(),
                            pf.Str(Meta.chapDelim) if Meta.chapters else pf.Span(),
                            table_no,
                            identifier=elem.identifier if elem.identifier else ""),
                    pf.Str(Meta.titleDelim)
                ]
            new_caption.append(
                pf.Span(identifier=elem.identifier +
                        '-c' if elem.identifier else ""))

            for elem1 in elem.caption.content[0].content:
                if isinstance(
                        elem1, pf.RawInline
                ) and elem1.format == 'tex' and elem1.text == r'\Caption2{tbl}':
                     # 第二题注
                    new_caption.append(pf.LineBreak)
                    if not ('-' in elem.classes or 'unnumbered' in elem.classes):
                        new_caption.extend([pf.Str(Meta.tableTitle2),
                                section_no if Meta.chapters else pf.Span(),
                                pf.Str(Meta.chapDelim) if Meta.chapters else pf.Span(),
                                table_no2,
                                pf.Str(Meta.titleDelim)])
                    new_caption.append(
                        pf.Span(identifier=elem.identifier +
                                '-sc' if elem.identifier else ""))
                    cap2_begin = True
                else:
                    pf.debug(elem1)
                    new_caption.append(elem1)
            pf.debug(new_caption)
            pf.debug(type(new_caption))
            elem.caption.content[0].content = pf.ListContainer(*new_caption)

            return elem

    def __init__(self):
        pass


def main(doc=None):
    replacer = TableCaptionReplace()
    return pf.run_filter(replacer.action, doc=doc)


if __name__ == "__main__":
    main()
