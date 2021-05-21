import panflute as pf
from .meta import Meta
import copy
import re
top_level = 1
equation_width = 0.7


class MathReplace():
    math_no = 1
    anchor_re = re.compile(r'{#([^}]+)}')

    def prepare(self, doc):
        self.meta = Meta(doc)
        self.top_level = self.meta.chaptersDepth if self.meta.chapters else ''
        self.section_no = pf.RawInline(
            f'''<w:fldSimple w:instr=" STYLEREF {self.top_level} \s"/>''', format="openxml")
        self.equation_no = pf.RawInline(
            f'''<w:fldSimple w:instr=" SEQ Equation \* ARABIC \s {self.top_level}"/>''',
            format="openxml")
        self.figure_no = pf.RawInline(
            f'''<w:fldSimple w:instr=" SEQ Figure \* ARABIC \s {self.top_level}"/>''',
            format="openxml")

    def action(self, elem, doc):
        # pf.debug('s:', elem)
        if not isinstance(elem, pf.Para):
            return
        rows = []
        content_group = []
        for elem1 in elem.content:
            if content_group and content_group[-1][0]:
                if isinstance(elem1, (pf.Space, pf.SoftBreak)):
                    continue
                elif isinstance(elem1, pf.Str) and isinstance(
                        content_group[-1][1][-1], pf.Math):
                    if elem1.text == '{}':
                        content_group[-1][1][-1] = (
                            content_group[-1][1][-1], None)
                        continue
                    elif elem1.text == '{.notag}' or elem1.text == '{-}':
                        content_group[-1][1][-1] = (
                            content_group[-1][1][-1], "")
                        continue
                    else:
                        match = self.anchor_re.fullmatch(elem1.text)
                        if match:
                            content_group[-1][1][-1] = (
                                content_group[-1][1][-1], match[1])
                            continue
            is_math = isinstance(elem1,
                                 pf.Math) and elem1.format == 'DisplayMath'
            if content_group:
                if content_group[-1][0] == is_math:
                    content_group[-1][1].append(elem1)
                    continue
            content_group.append([is_math, [elem1]])
        elem_old = elem

        # 开始生成输出表格
        elem = []
        first_para = True
        for elem_group in content_group:
            if not elem_group[0]:
                if not first_para:
                    elem_group[1] = [pf.RawInline('<w:pPr><w:ind w:firstLineChars="0" w:firstLine="0"/></w:pPr>', format="openxml"),
                                     *elem_group[1]]
                elem_new = pf.Para(*elem_group[1])
                elem.append(elem_new)
                first_para = False
                continue
            first_para = False
            rows = []
            for math_elem in elem_group[1]:
                if isinstance(math_elem, pf.Math):
                    math_elem = math_elem
                    notag = False
                    tag = ''
                else:
                    if isinstance(math_elem[1], str):
                        if math_elem[1]:
                            tag = math_elem[1]
                            notag = False
                        else:
                            tag = ''
                            notag = True
                            # pf.debug('notag')
                        math_elem = math_elem[0]
                    else:
                        math_elem = math_elem[0]
                        notag = False
                        tag = ''
                math_caption = [
                    pf.Str(self.meta.eqPrefix),
                    pf.Span(
                        self.section_no,
                        pf.Str(self.meta.chapDelim),
                        self.equation_no,
                        identifier=tag),
                    pf.Str(self.meta.eqSuffix)
                ] if not notag else []
                # 封装一行
                rows.extend([
                    *self.tableRow(
                        *self.tableCell(
                            self.tableCellPr(50 * (1 - equation_width)),
                            pf.Para(pf.Span())
                        ),
                        *self.tableCell(
                            self.tableCellPr(100 * equation_width),
                            pf.Div(pf.Para(math_elem),
                                   attributes={
                                'custom-style': 'Equation'
                            })),
                        *self.tableCell(
                            self.tableCellPr(50 * (1 - equation_width)),
                            pf.Div(pf.Para(pf.Span(), *math_caption),
                                   attributes={
                                'custom-style':
                                'Equation Caption'
                            }))
                    )])
                self.math_no += 1
            elem.extend(self.table(*rows))
            # pf.debug(elem)
        # pf.debug(elem)
        return elem

    @staticmethod
    def tableRow(*tableCell: pf.Block):
        return [pf.RawBlock('<w:tr>', format='openxml'),
                *tableCell,
                pf.RawBlock('</w:tr>', format='openxml')
                ]

    @staticmethod
    def tableCell(*blocks: pf.Block):
        return [pf.RawBlock('<w:tc>', format='openxml'),
                *blocks,
                pf.RawBlock('</w:tc>', format='openxml')
                ]

    @staticmethod
    def table(*tableRow: pf.Block):
        # tblPr > tblW 属性w:w="5000"以为表格总宽度为5000
        # tcPr > tcW 属性w:w="xxx" xxx换算为相对5000的百分比，故5000的15%为750
        # tblPr > tblLook 中对应表格的各项外观，这里使用第一列和最后一列两个参数来控制首尾
        return [pf.RawBlock('<w:tbl>', format='openxml'),
                pf.RawBlock('''
            <w:tblPr>
                <w:tblStyle w:val="EquationTable" />
                <w:tblW w:type="pct" w:w="5000" />
                <w:tblLook w:firstRow="0" w:lastRow="0" w:firstColumn="1" w:lastColumn="1" w:noHBand="0" w:noVBand="0" w:val="0000" />
            </w:tblPr>
            <w:tblGrid />
            ''', format='openxml'),
                *tableRow,
                pf.RawBlock('</w:tbl>', format='openxml'),
                ]

    @staticmethod
    def tableCellPr(width):
        return pf.RawBlock(
            f'<w:tcPr><w:tcW w:w="{50*int(width)}" w:type="pct"/></w:tcPr>',
            format="openxml")

    def __init__(self):
        pass


def main(doc=None):
    replacer = MathReplace()
    return pf.run_filter(replacer.action, prepare=replacer.prepare, doc=doc)


if __name__ == "__main__":
    main()
