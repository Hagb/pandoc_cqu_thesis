# find(): 对[xxx]{#abc}这样的写法标记书签
# replace(): 对[@xxx]这样的写法引用书签
# 可以实现对标题编号的引用
# 引用嵌套采用域代码的形式进行引用
# 写代码记得写注释！！！

import panflute as pf


def refNumStr(citationId: str):
    return pf.RawInline(f'<w:fldSimple w:instr=" REF {citationId} \\r \\h "/>',
                        format="openxml")


def refContentStr(citationId: str):
    return pf.RawInline(f'<w:fldSimple w:instr=" REF {citationId} \\h "/>',
                        format="openxml")


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
            if citationId.endswith('-page') and citationId[:-5] in self.bookmarks:
                # 引用页码
                elem = pf.RawInline(f'<w:fldSimple w:instr=" PAGEREF {citationId[:-5]} \\h "/>',
                                    format="openxml")
            elif ':' in citationId:
                # 有标识符，视为编号项
                preffix = citationId.split(':')[0]
                if citationId in self.bookmarks:
                    if preffix in ['eq', 'fig', 'tbl']:
                        # 在书签中，且前缀为eq,fig等，直接代入内容获取编号
                        elem = refContentStr(citationId)
                    else:
                        # 在书签中，常规编号项，sec，脚注等，引用编号
                        elem = refNumStr(citationId)
                elif citationId.endswith('-c') and citationId[:-2] in self.bookmarks:
                    # 不在书签中，但去掉后缀在，只能是常规编号项了，引用内容
                    elem = refContentStr(citationId[:-2])
            else:
                # 无标识符，默认书签表示引用内容
                if citationId in self.bookmarks:
                    # 引用内容
                    elem = refContentStr(citationId)
                elif citationId.endswith('-no'):
                    # 引用编号
                    elem = refNumStr(citationId[:-3])
        return elem

    def __init__(self):
        self.bookmarks = set()


def main(doc=None):

    refs_replacer = refsReplacer()
    return pf.run_filters([refs_replacer.find, refs_replacer.replace], doc=doc)


if __name__ == "__main__":
    main()
