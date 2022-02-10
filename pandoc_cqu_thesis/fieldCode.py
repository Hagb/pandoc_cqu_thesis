# 将 `{xxx}`{=field} 这样的写法转变为域代码
# 并且可以嵌套 `{Ref {Ref test_ref_ref}}`{=field}
# 借鉴自https://github.com/centixkadon/nju-thesis-markdown/blob/33bdc591d25f7b2a4fd96ea58bae450c2f99db9d/src/thesis.lua#L634

import panflute as pf

# fieldPrefix = """<w:fldChar w:fldCharType="begin"/><w:instrText xml:space="preserve">"""
# fieldSuffix = """</w:instrText><w:fldChar w:fldCharType="end"/>"""
# 通过匹配'{'和'}'中间的字符来实现
# TODO .replace('|', '')
# return pf.RawInline('<w:r>' + fieldStr.replace('{', fieldPrefix).replace('}', fieldSuffix) + '</w:r>', format='openxml')


class fieldCode():
    def action(self, elem, doc):
        if isinstance(elem, pf.RawInline):
            if elem.format in ["docx", "field"]:
                return pf.RawInline(self.genFieldXml(elem.text), format='openxml')
        if isinstance(elem, pf.RawBlock):
            if elem.format in ["docx", "field"]:
                return pf.RawBlock(self.genFieldXml(elem.text, isBlock=True), format='openxml')

    @staticmethod
    def genFieldXml(fieldStr: str, isBlock: bool = False):
        fieldStr: str = fieldStr.strip()
        if not (fieldStr.startswith('{') and fieldStr.endswith('}')):
            fieldStr = '{' + fieldStr + '}'
        result_str = "<w:p><w:r>" if isBlock else "<w:r>"
        temp_str = ""
        flag = True  # 用来标定域代码，False代表域代码的显示文本
        for s in fieldStr:
            if s not in ['{', '|', "}"]:
                temp_str += s
            elif s == '{':
                if len(temp_str) > 0:
                    result_str += """<w:instrText xml:space="preserve">%s</w:instrText>""" % temp_str
                result_str += """<w:fldChar w:fldCharType="begin"/>"""
                temp_str = ""
            elif s == '|':
                if flag and len(temp_str) > 0:
                    result_str += """<w:instrText xml:space="preserve">%s</w:instrText>""" % temp_str
                temp_str = ""
                flag = False
            elif s == '}':
                if flag == False:
                    result_str += """<w:fldChar w:fldCharType="separate"/>""" + \
                        """<w:t>%s</w:t>""" % temp_str
                    flag = True
                elif len(temp_str) > 0:
                    result_str += """<w:instrText xml:space="preserve">%s</w:instrText>""" % temp_str
                result_str += """<w:fldChar w:fldCharType="end"/>"""
                temp_str = ""
        return result_str + ("</w:r></w:p>" if isBlock else "</w:r>")


def main(doc=None, meta=None):
    replacer = fieldCode()
    return pf.run_filter(replacer.action, doc=doc)


if __name__ == "__main__":
    main()
