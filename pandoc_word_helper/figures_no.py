import panflute as pf
from .meta import Meta
import re


class FigCaptionReplace():
    math_no = 1
    anchor_re = re.compile(r'{#([^}]+)}')

    def action(self, elem, doc):

        # 若单独成段的图片没有题注，则对该段落应用Figure样式
        # 注：若采用\Style{xxx} ![]()的方式对单独成段的图片应用样式，该段代码则不会生效，故无需单独处理
        if isinstance(elem, pf.Para):
            if len(elem.content) == 1:
                if isinstance(elem.content[0], pf.Image):
                    if elem.content[0].title == "":
                        return pf.Div(elem, attributes={'custom-style': 'Figure'})

        if isinstance(elem, pf.Image):
            elem: pf.Image
            # pf.debug("Image!")

            # 若图片无题注，则直接返回图片，不做处理
            if elem.title == "":
                return elem

            if '-' in elem.classes or 'unnumbered' in elem.classes:
                new_content = []
            else:
                new_content = [
                    # 题注前缀
                    pf.Str(self.meta.figureTitle),
                    pf.Span(self.section_no,
                            pf.Str(self.chapDelim),
                            self.figure_no,
                            identifier=elem.identifier if elem.identifier else ""),
                    pf.Str(self.meta.titleDelim)
                ]
            new_content.append(
                pf.Span(identifier=elem.identifier +
                        ':c' if elem.identifier else ""))

            for elem1 in elem.content:
                if isinstance(
                        elem1, pf.RawInline
                ) and elem1.format == 'tex' and elem1.text == self.meta.secondCaptionSeparator:
                    # 第二题注
                    new_content.append(pf.LineBreak)
                    if not ('-' in elem.classes or 'unnumbered' in elem.classes):
                        new_content.extend([pf.Str(self.meta.figureTitle2),
                                            self.section_no,
                                            pf.Str(self.chapDelim),
                                            self.figure_no2,
                                            pf.Str(self.meta.titleDelim)])
                    new_content.append(
                        pf.Span(identifier=elem.identifier +
                                ':sc' if elem.identifier else ""))
                    cap2_begin = True
                else:
                    new_content[-1].content.append(elem1)
            elem.content = new_content

            return elem

    def prepare(self, doc):
        self.meta = Meta(doc)
        self.top_level = self.meta.chaptersDepth if self.meta.chapters else ''
        self.figSeqName = self.meta.figureTitle  # 题注前缀的文字和SEQ的内容相同，以便于在Word中产生相同的前缀
        self.chapDelim = self.top_level and self.meta.chapDelim
        self.section_no = pf.RawInline(
            self.top_level and
            f'''<w:fldSimple w:instr=" STYLEREF {self.top_level} \\s"/>''', format="openxml")
        self.figure_no = pf.RawInline(
            f'''<w:fldSimple w:instr=" SEQ {self.figSeqName} \\* ARABIC \\s {self.top_level}"/>''',
            format="openxml")
        self.figure_no2 = pf.RawInline(
            f'''<w:fldSimple w:instr=" SEQ {self.figSeqName} \\c \\* ARABIC \\s {self.top_level} "/>''',
            format="openxml")
        # 重复上一个编号

    def __init__(self):
        pass


def main(doc=None):
    replacer = FigCaptionReplace()
    return pf.run_filter(replacer.action, prepare=replacer.prepare, doc=doc)


if __name__ == "__main__":
    main()
