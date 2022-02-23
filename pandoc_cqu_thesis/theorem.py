import panflute as pf
from .meta import Meta, MetaFilter, metapreparemethod
from .Number import NumberFilter
from . import utils


class Theorem(MetaFilter, NumberFilter):
    def action(self, elem, doc):
        if isinstance(elem, pf.DefinitionList):
            content_result = []
            for content in elem.content:
                caption = content.term
                label = utils.stripLabel(caption)
                if not label:
                    content_result.append(pf.DefinitionList(content))
                    continue
                for i in self.meta.theorems:
                    if i in label['classes']:
                        thm = i
                        break
                else:
                    content_result.append(pf.DefinitionList(content))
                    continue

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

                numberinfo = self.getNumberingInfo(label)
                identifier = numberinfo['identifier']
                unnumber = not numberinfo['numbering']
                thm_number = [] if unnumber else [
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
                    # attributes={'custom-style': 'Definition Preffix'}
                )
                caption_elems = [] if not caption else [
                    pf.Str(self.meta.theoremPrefix),
                    pf.Span(
                        *caption,
                        identifier=identifier and (identifier + ':c'),
                        # attributes={'custom-style': 'Definition Title'}
                    ),
                    *reference,
                    pf.Str(self.meta.theoremSuffix)
                ]
                thm_header = pf.Div(pf.Para(
                    pf.Span() if not self.meta.combineDefinitionTerm else pf.RawInline(
                        r'<w:pPr><w:rPr><w:vanish/><w:specVanish/></w:rPr></w:pPr>', format='openxml'),
                    thm_prefix,
                    *caption_elems,
                    pf.Str(self.meta.theoremSeparator)),
                    attributes={'custom-style': 'Definition Term'}
                )
                thm_body = pf.Div(*[pf.Para(*i.content[0].content) if isinstance(i.content[0], pf.Plain)
                                    else i.content[0] for i in content.definitions],
                                  attributes={'custom-style': 'Definition'})

                content_result.append(thm_header)
                content_result.append(thm_body)
            return content_result

    @metapreparemethod
    def prepare(self, doc, meta):
        self.top_level = meta.chaptersDepth if meta.chapters else ''
        self.chapDelim = self.top_level and meta.chapDelim
        self.auto_labels = meta.autoThmLabels
        self.section_no = pf.RawInline(
            self.top_level and
            f'''<w:fldSimple w:instr=" STYLEREF {self.top_level} \\s"/>''', format="openxml")

    def theoremNumber(self, thm):
        return pf.RawInline(
            f'''<w:fldSimple w:instr=" SEQ {thm} \\* ARABIC \\s {self.top_level}"/>''',
            format="openxml")


def main(doc=None, meta=None):
    theorem = Theorem(meta=meta)
    return pf.run_filter(theorem.action, prepare=theorem.prepare, doc=doc)


if __name__ == "__main__":
    main()
