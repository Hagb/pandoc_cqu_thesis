# find(): 对[xxx]{#abc}这样的写法标记书签
# replace(): 对[@xxx]这样的写法引用书签
# 可以实现对标题编号的引用
# 引用嵌套采用域代码的形式进行引用
# 写代码记得写注释！！！

import panflute as pf


class refsReplacer():
    def find(self, elem, doc=None):
        if hasattr(elem, 'identifier') and elem.identifier:
            self.bookmarks.add(elem.identifier)
            # pf.debug('anchor:', elem.identifier)
        return elem

    def replace(self, elem, doc):
        if isinstance(elem, pf.Cite):
            elem: pf.Cite
            citation: pf.Citation = elem.citations[0]
            # pf.debug(citation.id)
            citationId: str = citation.id
            if ':' in citationId:
                # 有标识符，默认书签表示引用编号
                if citationId in self.bookmarks:
                    # 在书签中，无后缀，引用编号
                    elem = pf.RawInline(
                        f'<w:fldSimple w:instr=" REF {citationId} \\r \\h "/>',
                        format="openxml")
                elif citationId.endswith('-c'):
                    # 引用内容
                    elem = pf.RawInline(
                        f'<w:fldSimple w:instr=" REF {citationId[:-2]} \\h "/>',
                        format="openxml")
            else:
                # 无标识符，默认书签表示引用内容
                if citationId in self.bookmarks:
                    # 引用内容
                    elem = pf.RawInline(
                        f'<w:fldSimple w:instr=" REF {citationId} \\h "/>',
                        format="openxml")
                elif citationId.endswith('-no'):
                    # 引用编号
                    elem = pf.RawInline(f'<w:fldSimple w:instr=" REF {citationId[:-3]} \\r \\h "/>',
                                        format="openxml")
            if citationId.endswith('-page') and citationId[:-5] in self.bookmarks:
                # 引用页码
                elem = pf.RawInline(f'<w:fldSimple w:instr=" PAGEREF {citationId[:-5]} \\h "/>',
                                    format="openxml")
        return elem

    def __init__(self):
        self.bookmarks = set()


def main(doc=None):

    refs_replacer = refsReplacer()
    return pf.run_filters([refs_replacer.find, refs_replacer.replace], doc=doc)


if __name__ == "__main__":
    main()
