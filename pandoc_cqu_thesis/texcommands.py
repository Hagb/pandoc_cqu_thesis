import panflute as pf
import re
from .meta import MetaFilter

class ConstTexCommandReplace(MetaFilter):
    tex_re = re.compile(r'\\([^{ ]*)({.*})? ?')

    @classmethod
    def _parse_tex(self, tex_str, const_commands, function_commands, docinfo):
        re_result = self.tex_re.fullmatch(tex_str.strip())
        if re_result:
            name = re_result[1].lower()
            if name in function_commands:
                return function_commands[name](
                    re_result[2][1:-1], docinfo=docinfo) if re_result[2] \
                    else function_commands[re_result[1]](docinfo=docinfo)
            elif name in const_commands:
                return const_commands[name]

    def action(self, elem, doc: pf.Doc):
        docinfo = [elem, doc, self.meta]
        if isinstance(elem, pf.RawBlock):
            new_elem = self._parse_tex(
                elem.text, self.block_const_commands, self.block_function_commands, docinfo)
            if new_elem:
                return new_elem
            else:
                new_elem = self._parse_tex(
                    elem.text, self.inline_const_commands, self.inline_function_commands, docinfo)
                if isinstance(new_elem, list):
                    return pf.Para(*new_elem)
                elif new_elem:
                    return pf.Para(new_elem)
        elif isinstance(elem, pf.RawInline):
            return self._parse_tex(elem.text, self.inline_const_commands, self.inline_function_commands, docinfo)

        return elem

    def __init__(self, inline_const_commands={}, inline_function_commands={},
                 block_const_commands={}, block_function_commands={}, meta=None):
        self.inline_const_commands = {name.lower(): inline_const_commands[name]
                                      for name in inline_const_commands}
        self.inline_function_commands = {name.lower(): inline_function_commands[name]
                                         for name in inline_function_commands}
        self.block_const_commands = {name.lower(): block_const_commands[name]
                                     for name in block_const_commands}
        self.block_function_commands = {name.lower(): block_function_commands[name]
                                        for name in block_function_commands}
        super().__init__(meta)
