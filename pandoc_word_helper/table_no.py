import panflute as pf
from .meta import Meta
import re


class TableCaptionReplace():
    def __init__(self):
        top_level = Meta.chaptersDepth if Meta.chapters else ''
        tableSeqName = Meta.tableTitle  # 题注前缀的文字和SEQ的内容相同，以便于在Word中产生相同的前缀
        self.anchor_re = re.compile(r'{#([^}]+)}')

        self.section_no = pf.RawInline(
            f'''<w:fldSimple w:instr=" STYLEREF {top_level} \s"/>''', format="openxml")
        self.table_no = pf.RawInline(
            f'''<w:fldSimple w:instr=" SEQ {tableSeqName} \* ARABIC \s {top_level}"/>''',
            format="openxml")
        self.table_no2 = pf.RawInline(
            f'''<w:fldSimple w:instr=" SEQ {tableSeqName} \c \* ARABIC \s {top_level} "/>''',
            format="openxml")
        # 重复上一个编号

    def generateTableNumber(self, identifier=''):
        # 创建表格编号
        return [
            pf.Str(Meta.tableTitle),
            pf.Span(self.section_no if Meta.chapters else pf.Span(),
                    pf.Str(Meta.chapDelim) if Meta.chapters else pf.Span(),
                    self.table_no,
                    identifier=identifier),
            pf.Str(Meta.titleDelim)
        ]

    def generateTableNumber2(self, identifier=''):
        # 创建表格编号
        return [
            pf.Str(Meta.tableTitle2),
            pf.Span(self.section_no if Meta.chapters else pf.Span(),
                    pf.Str(Meta.chapDelim) if Meta.chapters else pf.Span(),
                    self.table_no2,
                    ),
            pf.Str(Meta.titleDelim)
        ]

    def isSecondCaptionSeparator(self, item):
        return isinstance(item, pf.RawInline) and item.format == 'tex' and item.text == r'\Caption2{tbl}'

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

            # 判断是否编号
            # TODO 在这里检测是否需要编号，是否存在标签，以及去掉标签返回剩下的内容
            isNeedNumber = True
            hasIdentifier = False
            captionStr: str = pf.stringify(elem.caption)  # 这里得到题注的纯文本
            if captionStr.endswith("{-}"):
                isNeedNumber = False
            identifier = ""  # 从上面获取到标签，以供下面使用

            # 获取题注元素
            captionContent = elem.caption.content[0].content

            # 判断是否存在第二题注
            for item in captionContent:
                if self.isSecondCaptionSeparator(item) and item.index < len(captionContent):
                    # 只有当第二题注的分隔符后面还有元素的时候，才算存在第二题注
                    hasSecondCaption = True
                    secondCaptionIndex = item.index
                    break
            # 生成二级题注
            if hasSecondCaption:
                firstCaption = pf.Span(*captionContent[:secondCaptionIndex], identifier=identifier+"-c" if hasIdentifier else '')
                secondCaption = pf.Span(*captionContent[secondCaptionIndex+1:], identifier=identifier+'-sc' if hasIdentifier else '')
            else:
                firstCaption = pf.Span(*captionContent, identifier=identifier+"-c" if hasIdentifier else '')

            # 生成新的题注内容
            new_caption = []
            if isNeedNumber:
                new_caption.extend(self.generateTableNumber(identifier))
            new_caption.append(firstCaption)
            if hasSecondCaption:
                new_caption.append(pf.LineBreak())
                if isNeedNumber:
                    new_caption.extend(self.generateTableNumber2(identifier))
                new_caption.append(secondCaption)

            elem.caption.content[0].content = pf.ListContainer(*new_caption)

            return elem


def main(doc=None):
    replacer = TableCaptionReplace()
    return pf.run_filter(replacer.action, doc=doc)


if __name__ == "__main__":
    main()
