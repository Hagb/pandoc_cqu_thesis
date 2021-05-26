import panflute as pf
from .meta import Meta
from . import utils


class Theorem():
    def action(self, elem, doc):
        if isinstance(elem, pf.DefinitionList):
            caption = elem.content[0].term
            label = utils.stripLabel(caption)
            if not label:
                return
            for i in self.meta.theorems:
                if i in label['classes']:
                    thm = i
                    break
            else:
                return

            reference = []
            for i in caption[::-1]:
                if isinstance(i, pf.Cite):
                    reference.append(i)
                    caption.pop()
                elif isinstance(i, pf.Space):
                    caption.pop()
                else:
                    break
            reference = reference[::-1]

            identifier = label['identifier'] or ''
            nonumber = 'nonumbered' in label['classes']
            thm_number = [] if nonumber else [
                # pf.Space,
                pf.Span(
                    self.section_no,
                    pf.Str(self.chapDelim),
                    self.theoremNumber(thm),
                    identifier=identifier,
                    attributes={'_prefix': self.meta.theorems[thm]}
                ),
                # pf.Space
            ]
            thm_prefix = pf.Span(
                pf.Str(self.meta.theorems[thm]),
                *thm_number,
                attributes={'custom-style': 'Definition Preffix'}
            )
            caption_elems = [] if not caption else [
                pf.Str(self.meta.theoremPrefix),
                pf.Span(
                    *caption,
                    identifier=identifier and (identifier + ':c'),
                    attributes={'custom-style': 'Definition Title'}
                ),
                *reference,
                pf.Str(self.meta.theoremSuffix)
            ]
            thm_body = [pf.Para(*i.content[0].content) if isinstance(i.content[0], pf.Plain)
                        else i.content[0] for i in elem.content[0].definitions]
            thm_header = pf.Para(thm_prefix,
                                 *caption_elems,
                                 pf.Str(self.meta.theoremSeparator))
            if isinstance(thm_body[0], pf.Para):
                thm_header.content.extend(thm_body[0].content)
                thm_body = thm_body[1:]
            return pf.Div(thm_header, *thm_body, attributes={'custom-style': 'Definition'})

    def prepare(self, doc):
        self.meta = Meta(doc)
        self.top_level = self.meta.chaptersDepth if self.meta.chapters else ''
        self.chapDelim = self.top_level and self.meta.chapDelim
        self.section_no = pf.RawInline(
            self.top_level and
            f'''<w:fldSimple w:instr=" STYLEREF {self.top_level} \\s"/>''', format="openxml")

    def theoremNumber(self, thm):
        return pf.RawInline(
            f'''<w:fldSimple w:instr=" SEQ {thm} \\* ARABIC \\s {self.top_level}"/>''',
            format="openxml")


def main(doc=None):
    theorem = Theorem()
    return pf.run_filter(theorem.action, prepare=theorem.prepare, doc=doc)


if __name__ == "__main__":
    main()
