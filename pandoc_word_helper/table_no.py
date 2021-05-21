import panflute as pf
from .meta import Meta
from . import utils


class TableCaptionReplace():
    def prepare(self, doc):
        self.meta = Meta(doc)
        self.top_level = self.meta.chaptersDepth if self.meta.chapters else ''
        self.tableSeqName = self.meta.tableTitle  # 题注前缀的文字和SEQ的内容相同，以便于在Word中产生相同的前缀

        self.section_no = pf.RawInline(
            f'''<w:fldSimple w:instr=" STYLEREF {self.top_level} \\s"/>''', format="openxml")
        self.table_no = pf.RawInline(
            f'''<w:fldSimple w:instr=" SEQ {self.tableSeqName} \\* ARABIC \\s {self.top_level}"/>''',
            format="openxml")
        self.table_no2 = pf.RawInline(
            f'''<w:fldSimple w:instr=" SEQ {self.tableSeqName} \\c \\* ARABIC \\s {self.top_level} "/>''',
            format="openxml")
            # 重复上一个编号

    def generateTableNumber(self, identifier=''):
        # 创建表格编号
        return [
            pf.Str(self.meta.tableTitle),
            pf.Span(self.section_no if self.meta.chapters else pf.Span(),
                    pf.Str(self.meta.chapDelim) if self.meta.chapters else pf.Span(),
                    self.table_no,
                    identifier=identifier),
            pf.Str(self.meta.titleDelim)
        ]

    def generateTableNumber2(self, identifier=''):
        # 创建表格编号
        return [
            pf.Str(self.meta.tableTitle2),
            pf.Span(self.section_no if self.meta.chapters else pf.Span(),
                    pf.Str(self.meta.chapDelim) if self.meta.chapters else pf.Span(),
                    self.table_no2,
                    ),
            pf.Str(self.meta.titleDelim)
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
                return [elem, pf.Para(pf.Span()) if self.meta.isParaAfterTable else pf.Null()]

            # 获取题注元素
            captionContent = elem.caption.content[0].content

            # 判断是否编号
            # TODO 在这里检测是否需要编号，是否存在标签，以及去掉标签返回剩下的内容
            isNeedNumber = True  # 这里得到题注的纯文本
            identifier = ""
            Label = utils.stripLabel(captionContent)
            if Label:
                identifier = Label['identifier']
                isNeedNumber = 'nonumbered' not in Label['classes']

            # 判断是否存在第二题注
            for item in captionContent:
                if self.isSecondCaptionSeparator(item) and item.index < len(captionContent):
                    # 只有当第二题注的分隔符后面还有元素的时候，才算存在第二题注
                    hasSecondCaption = True
                    secondCaptionIndex = item.index
                    break
            else:
                hasSecondCaption = False

            # 生成两级题注的文本内容
            if hasSecondCaption:
                firstCaption = pf.Span(
                    *captionContent[:secondCaptionIndex], identifier=identifier+"-c" if identifier else '')
                secondCaption = pf.Span(
                    *captionContent[secondCaptionIndex+1:], identifier=identifier+'-sc' if identifier else '')
            else:
                firstCaption = pf.Span(
                    *captionContent, identifier=identifier+"-c" if identifier else '')

            # 用两级题注的内容和表格编号生成新的题注内容
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

            return [elem, pf.Para(pf.Span()) if self.meta.isParaAfterTable else pf.Null()]


def main(doc=None):
    replacer = TableCaptionReplace()
    return pf.run_filter(replacer.action, prepare=replacer.prepare, doc=doc)


if __name__ == "__main__":
    main()
