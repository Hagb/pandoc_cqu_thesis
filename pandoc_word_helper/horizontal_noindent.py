import panflute as pf
import sys

def horizontalNoindentAction(elem, doc):
    if isinstance(elem, pf.HorizontalRule):
        return pf.Div(
            pf.Para(
                pf.RawInline(
                    '<w:r><w:pict>'
                    '<v:rect style="width:0;height:1.5pt" o:hralign="center" o:hrstd="t" o:hr="t" />'
                    '</w:pict></w:r>', format="openxml")
            ), attributes={'custom-style': 'noindent'})


def main(doc=None, meta=None):
    return pf.run_filter(horizontalNoindentAction, doc=doc)


if __name__ == '__main__':
    sys.exit(main())
