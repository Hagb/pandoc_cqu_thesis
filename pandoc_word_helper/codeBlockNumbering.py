# 对代码块添加行号，通过把代码块拆分成若干代码行实现

import panflute as pf
from .meta import Meta


class CodeBlockNumbering():
    def action(self, elem, doc):
        if isinstance(elem, pf.CodeBlock):
            elem: pf.CodeBlock
            s = elem.text
            codeClass = elem.classes
            return pf.OrderedList(*[pf.ListItem(pf.CodeBlock(i, classes=codeClass)) for i in s.split('\n')])

    def __init__(self) -> None:
        pass


def main(doc=None):
    if Meta.codeBlockNumbering:
        replacer = CodeBlockNumbering()
        return pf.run_filter(replacer.action, doc=doc)


if __name__ == "__main__":
    main()
