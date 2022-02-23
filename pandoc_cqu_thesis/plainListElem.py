import panflute as pf
import sys


class plainListElemWorkaround():
    def action(self, elem, doc):
        if isinstance(elem, (pf.DefinitionList, pf.BulletList, pf.OrderedList)):
            for list_item in elem.content:
                self._plainify(list_item)

    @classmethod
    def _plainify(self, elem):
        content = elem.container if isinstance(elem, pf.DefinitionItem) else elem.content
        for n, e in enumerate(content):
            if isinstance(e, pf.Div) and '_eqn' not in e.classes:
                self._plainify(e)
            elif isinstance(e, (pf.Para, pf.Plain)):
                elem.content[n] = pf.Para(
                    pf.RawInline(
                        '''<w:pPr><w:ind w:firstLineChars="0"/></w:pPr>''',
                        format="openxml"),
                    *e.content
                )


def main(doc=None, meta=None):
    replacer = plainListElemWorkaround()
    return pf.run_filter(replacer.action, doc=doc)


if __name__ == '__main__':
    sys.exit(main())
