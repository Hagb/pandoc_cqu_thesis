import panflute as pf
import sys


class plainListElemWorkaround():
    def action(self, elem, doc):
        if isinstance(elem, pf.ListItem):
            self.plainify(elem)

    @classmethod
    def plainify(self, elem):
        for n, e in enumerate(elem.content):
            if isinstance(e, pf.Div):
                self.plainify(e)
            elif isinstance(e, pf.Para):
                elem.content[n] = pf.Plain(*e.content)


def main(doc=None, meta=None):
    replacer = plainListElemWorkaround()
    return pf.run_filter(replacer.action, doc=doc)


if __name__ == '__main__':
    sys.exit(main())
