import regex
import panflute as pf
_attr_regex = r'(?:#([^ \{\}]+)|(\.[^ \{\}]+|-))'
attrs_regex = r'\{\s*' + f'(?:{_attr_regex}\\s+)*{_attr_regex}' + r'\s*\}'
anchor_re = regex.compile('^.* ' + attrs_regex + r'\s*$')


def stripLabel(elems):
    match = anchor_re.match(''.join(pf.stringify(elem) for elem in elems))
    if match:
        while '{' not in pf.stringify(elems.pop()):
            pass
        return {
            'identifier': match[1+2] or match[1],
            'classes': [i[1:] or 'nonumbered' for i in match.captures(2) + match.captures(2+2)],
        }
