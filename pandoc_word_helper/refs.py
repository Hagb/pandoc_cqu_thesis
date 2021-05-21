# find(): 找出文档中所有的书签
# replace(): 对[@xxx]这样的写法引用书签
# 可以实现对标题编号的引用
# 引用嵌套采用域代码的形式进行引用，不在这里处理
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
        # 获取所有书签
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
            if citationId not in self.bookmarks:
            # 如果不在书签列表中，只有3种情况
            # 有":page"后缀
            # 有":c"后缀
            # 有":no"后缀
            # 其余情况全部不管，原路返回
                # 如果以":page"结尾，说明是引用页码
                if citationId.endswith(':page') and citationId[:-5] in self.bookmarks:
                    elem = pf.RawInline(f'<w:fldSimple w:instr=" PAGEREF {citationId[:-5]} \\h "/>',
                                        format="openxml")
                # 如果以":c"结尾，虽然不在书签中，但去掉":c"后存在该书签，说明是对标题或者编号段落等引用内容
                # 引用内容调用refContentStr
                elif citationId.endswith(':c') and citationId[:-2] in self.bookmarks:
                    elem = refContentStr(citationId[:-2])
                elif citationId.endswith(':sc') and citationId[:-3] in self.bookmarks:
                    elem = refContentStr(citationId[:-3])
                # 如果以":no"结尾，虽然不在书签中，但去掉后缀后在书签中，表示强制调用标题等编号段落的编号
                elif citationId.endswith(':no') and citationId[:-3] in self.bookmarks:
                    elem = refNumStr(citationId[:-3])
            else:
            # 如果在书签列表中
            # 如果":"不在字符串中，说明没有前缀也没有后缀，那么只能以书签内容作为内容进行引用，避免出错
                # 可能是**最常规的书签引用**的内容
                # 可能是没有加前缀的题注的编号
                # 可能是没有前缀的编号段落的段落内容（这种情况下只能通过"xxx:no"的形式进行引用得到编号）
                if ':' not in citationId:
                    elem = refContentStr(citationId)
            # 那么现在只剩下有前后缀的情况，前后缀可能认识或者不认识
            # 认识的后缀只剩这一种情况
                # 如果以":c"或者":sc"结尾，且直接就存在该书签，说明是对图片表格等题注内容进行引用
                # 直接以内容refContentStr返回书签
                elif citationId.endswith(':c') or citationId.endswith(':sc'):
                    elem = refContentStr(citationId)
            # 认识的前缀有两种情况
            # 1. 可能是题注等以内容作为编号的情况，需要返回其内容
                # TODO 根据不同的引用语法返回不同的“前缀字符”，只有存在正确的前缀的情况下，才能在引用的时候返回“前缀字符”
                elif citationId.split(':')[0] in self.knownContentPrefix:
                        elem = refContentStr(citationId)
            # 2. 可能是标题等编号段落，需要返回其编号
                elif citationId.split(':')[0] in self.knownNumPrefix:
                    elem = refNumStr(citationId)
            # 剩下前缀后缀都不认识的情况
                # 直接返回对内容的引用
                else:
                    elem = refContentStr(citationId)
        return elem

    def __init__(self):
        self.bookmarks = set()
        # 已知的以书签“内容”作为编号的前缀
        self.knownContentPrefix = ['eq', 'fig', 'tbl', 'def', 'thm']
        # 已知的以书签“内容”作为“内容”的前缀
        self.knownNumPrefix = ['lst', 'sec']


def main(doc=None):

    refs_replacer = refsReplacer()
    return pf.run_filters([refs_replacer.find, refs_replacer.replace], doc=doc)


if __name__ == "__main__":
    main()
