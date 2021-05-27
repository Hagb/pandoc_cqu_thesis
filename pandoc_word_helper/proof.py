import panflute as pf
from panflute.tools import _get_metadata
from .meta import Meta, MetaFilter
from . import utils
from . import word_elements


class Proof(MetaFilter):
    def action(self, elem, doc):
        if isinstance(elem, pf.Div) and 'proof' in elem.classes:
            proof_header = pf.Div(pf.Para(
                pf.Span() if not self.meta.combineDefinitionTerm else pf.RawInline(
                    r'<w:pPr><w:rPr><w:vanish/><w:specVanish/></w:rPr></w:pPr>', format='openxml'),
                pf.Span(pf.Str(self.meta.proof),
                        # attributes={'custom-style': 'Definition Preffix'}
                        )
            ), attributes={'custom-style': 'Definition Term'})

            # 生成证毕符号，这里允许证毕符号使用完整的Markdown语法来套用样式
            if self.meta.proofQed != '':
                qed = [word_elements.inline_const_commands['tabR']]
                if doc.get_metadata().get('proofQed') and isinstance(doc.metadata['proofQed'], pf.MetaInlines):
                    qed.extend(doc.metadata['proofQed'].content)
                else:
                    qed.append(pf.Str(self.meta.proofQed))
            else:
                qed = []

            if isinstance(elem.content[-1], pf.Para):
                elem.content[-1].content.extend(qed)
            else:
                elem.content.append(pf.Para(*qed))
            proof_body = pf.Div(
                *elem.content, attributes={'custom-style': 'Definition'})
            return [proof_header, proof_body]


def main(doc=None, meta=None):
    proof = Proof(meta=meta)
    return pf.run_filter(proof.action, prepare=proof.prepare, doc=doc)


if __name__ == "__main__":
    main()
