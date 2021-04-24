import panflute as pf
from .meta import Meta
import re
top_level = Meta.chaptersDepth if Meta.chapters else ''
figSeqName = Meta.figureTitle # 题注前缀的文字和SEQ的内容相同，以便于在Word中产生相同的前缀

section_no = pf.RawInline(
    f'''<w:fldSimple w:instr=" STYLEREF {top_level} \s"/>''', format="openxml")
figure_no = pf.RawInline(
    f'''<w:fldSimple w:instr=" SEQ {figSeqName} \* ARABIC \s {top_level}"/>''',
    format="openxml")
figure_no2 = pf.RawInline(
    f'''<w:fldSimple w:instr=" SEQ {figSeqName} \c \* ARABIC \s {top_level} "/>''',
    format="openxml")
    # 重复上一个编号


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
                    pf.Str(Meta.figureTitle),
                    pf.Span(section_no if Meta.chapters else pf.Span(),
                            pf.Str(Meta.chapDelim) if Meta.chapters else pf.Span(),
                            figure_no,
                            identifier=elem.identifier if elem.identifier else ""),
                    pf.Str(Meta.titleDelim)
                ]
            new_content.append(
                pf.Span(identifier=elem.identifier +
                        '-c' if elem.identifier else ""))

            for elem1 in elem.content:
                if isinstance(
                        elem1, pf.RawInline
                ) and elem1.format == 'tex' and elem1.text == r'\Caption2{fig}':
                     # 第二题注
                    new_content.append(pf.LineBreak)
                    if not ('-' in elem.classes or 'unnumbered' in elem.classes):
                        new_content.extend([pf.Str(Meta.figureTitle2),
                                section_no if Meta.chapters else pf.Span(),
                                pf.Str(Meta.chapDelim) if Meta.chapters else pf.Span(),
                                figure_no2,
                                pf.Str(Meta.titleDelim)])
                    new_content.append(
                        pf.Span(identifier=elem.identifier +
                                '-sc' if elem.identifier else ""))
                    cap2_begin = True
                else:
                    new_content[-1].content.append(elem1)
            elem.content = new_content

            return elem

    def __init__(self):
        pass


def main(doc=None):
    replacer = FigCaptionReplace()
    return pf.run_filter(replacer.action, doc=doc)


if __name__ == "__main__":
    main()
