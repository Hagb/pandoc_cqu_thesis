# 处理代码块
# 1. 用“␣”符号替换代码中的“空格”，以增强视觉效果（需要字体支持字符U+2423）
# 2. 对代码块添加行号，通过把代码块拆分成若干代码行实现

import panflute as pf
from .meta import Meta, MetaFilter


class CodeBlock(MetaFilter):
    def action(self, elem, doc):
        if isinstance(elem, (pf.CodeBlock, pf.Code)):
            elem = self.codeSpaceVisible(elem)
        if isinstance(elem, pf.CodeBlock):
            elem = self.codeBlockNumbering(elem)
        return elem

    def codeBlockNumbering(self, elem):
        elem: pf.CodeBlock
        s = elem.text
        codeClass = elem.classes
        if self.meta.codeBlockNumbering:
            lines = s.split('\n')
            if len(lines) > self.meta.codeBlockNumberingMinLine:
                return pf.OrderedList(*[pf.ListItem(pf.CodeBlock(line, classes=codeClass)) for line in lines])
        return elem

    def codeSpaceVisible(self, elem):
        if self.meta.codeSpaceVisible:
            elem.text = elem.text.replace(' ', '␣')
        return elem


def main(doc=None, meta=None):
    replacer = CodeBlock(meta=meta)
    return pf.run_filter(replacer.action, prepare=replacer.prepare, doc=doc)


if __name__ == "__main__":
    main()
