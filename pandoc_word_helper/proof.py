import panflute as pf
from .meta import Meta
from . import utils
from . import word_elements


class Proof():
    def action(self, elem, doc):
        if isinstance(elem, pf.Div) and 'proof' in elem.classes:
            proof_header = pf.Para(
                pf.Span(pf.Str(self.meta.proof), attributes={
                        'custom-style': 'Definition Preffix'}),
            )
            if isinstance(elem.content[0], pf.Para):
                proof_header.content.extend(elem.content[0].content)
                elem.content = elem.content[1:]
            qed = [word_elements.inline_const_commands['tabR'],
                   pf.Str(self.meta.proofQed)]
            if isinstance(elem.content[-1], pf.Para):
                elem.content[-1].content.extend(qed)
            else:
                elem.content.append(pf.Para(*qed))
            proof_body = pf.Div(
                *elem.content, attributes={'custom-style': 'Definition'})
            return [proof_header, proof_body]

    def prepare(self, doc):
        self.meta = Meta(doc)


def main(doc=None):
    proof = Proof()
    return pf.run_filter(proof.action, prepare=proof.prepare, doc=doc)


if __name__ == "__main__":
    main()
