from .meta import Meta, MetaFilter, metapreparemethod
# find(): 找出文档中所有的书签
# replace(): 对[@xxx]这样的写法引用书签
# 可以实现对标题编号的引用
# 引用嵌套采用域代码的形式进行引用，不在这里处理
# 写代码记得写注释！！！

import panflute as pf


def refNumStr(citationId: str):
    return pf.RawInline(f'<w:fldSimple w:instr=" REF {citationId} \\r \\h \\t "/>',
                        format="openxml")


def refContentStr(citationId: str):
    return pf.RawInline(f'<w:fldSimple w:instr=" REF {citationId} \\h "/>',
                        format="openxml")


def refPage(citationId):
    return pf.RawInline(f'<w:fldSimple w:instr=" PAGEREF {citationId} \\h "/>',
                        format="openxml")


class refsReplacer(MetaFilter):
    @metapreparemethod
    def prepare(self, doc, meta):
        self.bookmarks = set()
        self.bookmarks_custom = {}
        # 已知的以书签“内容”作为编号的前缀
        self.knownContentPrefix = {
            'eq': meta.eqnPrefix,
            'fig': meta.figPrefix,
            'tbl': meta.tblPrefix,
            # 'def':meta.?
        }
        self.knownContentSuffix = {
            'eq': meta.eqnSuffix,
            'fig': meta.figSuffix,
            'tbl': meta.tblSuffix,
            # 'def':meta.?
        }
        # 已知的以书签“内容”作为“内容”的前缀
        self.knownNumPrefix = {
            'lst': meta.lstPrefix,
            'sec': meta.secPrefix
        }
        self.knownNumSuffix = {
            'lst': meta.lstSuffix,
            'sec': meta.secSuffix
        }

    def find(self, elem, doc=None):
        # 获取所有书签
        if getattr(elem, 'identifier', ''):
            prefix = getattr(elem, 'attributes', {}).get('_prefix', '')
            suffix = getattr(elem, 'attributes', {}).get('_suffix', '')
            if prefix or suffix:
                self.bookmarks_custom[elem.identifier] = [prefix, suffix]
            else:
                self.bookmarks.add(elem.identifier)
            # pf.debug('anchor:', elem.identifier)

    def replace(self, elem, doc):
        if not isinstance(elem, pf.Cite):
            return
        elem: pf.Cite
        results = []
        for n, citation in enumerate(elem.citations):
            # pf.debug(citation.id)
            citationId: str = citation.id
            """
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
            """
            result = []
            prefix = ''
            suffix = ''
            label_parts = citationId.split(':')
            if citationId in self.bookmarks_custom:
                prefix, suffix = self.bookmarks_custom[citationId]
                result = [
                    refContentStr(citationId)
                ]
            elif len(label_parts) >= 3 and label_parts[-1] in ('sc', 'c'):
                if label_parts[0] in self.knownNumPrefix:
                    result = [refContentStr(':'.join(label_parts[:-1]))]
                else:
                    result = [refContentStr(citationId)]
            elif len(label_parts) >= 2:
                if label_parts[-1] == 'page':
                    prefix = self.meta.pagePrefix
                    suffix = self.meta.pageSuffix
                    result = [refPage(':'.join(label_parts[:-1]))]
                elif label_parts[-1] == 'no':
                    prefix = self.knownNumPrefix['sec']
                    suffix = self.knownNumSuffix['sec']
                    result = [refNumStr(':'.join(label_parts[:-1]))]
                elif label_parts[0] in self.knownNumPrefix:
                    prefix = self.knownNumPrefix[label_parts[0]]
                    suffix = self.knownNumSuffix[label_parts[0]]
                    result = [refNumStr(citationId)]
                elif label_parts[0] in self.knownContentPrefix:
                    prefix = self.knownContentPrefix[label_parts[0]]
                    suffix = self.knownContentSuffix[label_parts[0]]
                    result = [
                        refContentStr(citationId)
                    ]
            if not result:
                if citationId in self.bookmarks:
                    result = [refContentStr(citationId)]
                else:
                    if results and isinstance(results[-1], pf.Cite):
                        results[-1].citations.append(citation)
                    else:
                        cite = pf.Cite()
                        cite.citations.append(citation)
                        if n:
                            results.extend([pf.Str(','), pf.Space])
                        results.append(cite)
                    continue
            if n:
                results.extend([pf.Str(','), pf.Space])
            if citation.mode == 'SuppressAuthor' or citation.prefix or citation.suffix:
                prefix = ""
                suffix = ""
            results.extend(
                [*citation.prefix,
                 pf.Str(prefix),
                 *result,
                 pf.Str(suffix),
                 *citation.suffix]
            )
        return results


def main(doc=None, meta=None):
    refs_replacer = refsReplacer(meta=meta)
    return pf.run_filters([refs_replacer.find, refs_replacer.replace], prepare=refs_replacer.prepare, doc=doc)


if __name__ == "__main__":
    main()
