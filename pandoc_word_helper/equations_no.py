import panflute as pf
from .meta import Meta
import copy
import re
from . import utils
top_level = 1
equation_width = 0.7


class MathReplace():
    math_no = 1

    def prepare(self, doc):
        self.meta = Meta(doc)
        self.top_level = self.meta.chaptersDepth if self.meta.chapters else ''
        self.chapDelim = self.top_level and self.meta.chapDelim
        self.section_no = pf.RawInline(
            self.top_level and
            f'''<w:fldSimple w:instr=" STYLEREF {self.top_level} \\s"/>''', format="openxml")
        self.equation_no = pf.RawInline(
            f'''<w:fldSimple w:instr=" SEQ Equation \\* ARABIC \\s {self.top_level}"/>''',
            format="openxml")
        self.auto_labels = self.meta.autoEqnLabels

    def action(self, elem, doc):
        # pf.debug('s:', elem)
        if not isinstance(elem, (pf.Para, pf.Plain)):
            return
        origin_type = type(elem)
        rows = []
        content_group = []
        n = 0
        while n < len(elem.content):
            elem1 = elem.content[n]
            if content_group and content_group[-1][0] and \
                    isinstance(elem1, (pf.Space, pf.SoftBreak)):
                n += 1
                continue
            is_math = isinstance(elem1,
                                 pf.Math) and elem1.format == 'DisplayMath'
            if not is_math and content_group and content_group[-1][0] and \
                    isinstance(content_group[-1][1][-1], pf.Math):
                attrs = utils.stripLabel(
                    elem.content[n:], tail=False, strip_inplace=False)
                if attrs:
                    has_tag_attr = self.auto_labels and \
                        not ('notag' in attrs['classes'] or 'nonumbered' in attrs['classes']) or \
                        'tag' in attrs['classes']
                    attr = attrs['identifier'] if has_tag_attr or attrs['identifier'] else None
                    content_group[-1][1][-1] = (content_group[-1][1][-1], attr)
                    n += attrs['strip_len']
                    continue
            n += 1
            if content_group:
                if content_group[-1][0] == is_math:
                    content_group[-1][1].append(elem1)
                    continue
            content_group.append([is_math, [elem1]])
        if len(content_group) == 1 and not content_group[0][0]:
            return
        parent_elem = elem
        noindent = isinstance(elem, pf.Para)
        while parent_elem:
            if isinstance(parent_elem, (pf.TableCell)):
                return
            if isinstance(parent_elem, (pf.ListItem, pf.DefinitionItem)):
                noindent = False
                pf.debug(elem)
            parent_elem = parent_elem.parent

        # 开始生成输出表格
        elem = []
        first_para = True
        for elem_group in content_group:
            if not elem_group[0]:
                if noindent and not first_para:
                    elem_group[1] = [
                        pf.RawInline(
                            '<w:pPr><w:ind w:firstLineChars="0" w:firstLine="0"/></w:pPr>', format="openxml"),
                        *elem_group[1]
                    ]
                elem_new = origin_type(*elem_group[1])
                elem.append(elem_new)
                first_para = False
                continue
            first_para = False
            rows = []
            for math_elem in elem_group[1]:
                if isinstance(math_elem, pf.Math):
                    math_elem = math_elem
                    notag = not self.auto_labels
                    tag = ''
                else:
                    if isinstance(math_elem[1], str):
                        notag = False
                        tag = math_elem[1]
                    else:
                        notag = True
                        tag = ''
                    math_elem = math_elem[0]
                math_caption = [
                    pf.Str(self.meta.eqPrefix),
                    pf.Span(
                        self.section_no,
                        pf.Str(self.chapDelim),
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
