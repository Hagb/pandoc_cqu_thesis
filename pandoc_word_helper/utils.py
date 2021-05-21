import regex
import panflute as pf
_attr_regex = r'(?:#([^ \{\}]+)|(\.[^ \{\}]+|-))'
attrs_regex = r'\{\s*' + f'(?:{_attr_regex}\\s+)*{_attr_regex}' + r'\s*\}'
anchor_re = regex.compile('^' + attrs_regex + r'\s*$')


def stripLabel(elems):
    label_strs = []
    for i in elems[::-1]:
        if isinstance(i, (pf.Space, pf.Str)):
            label_strs.append(pf.stringify(i))
            if label_strs[-1].startswith('{'):
                break
        else:
            return
    match = anchor_re.match(''.join(label_strs[::-1]))
    if match:
        for i in range(len(label_strs)):
            elems.pop()
        for i in elems[::-1]:
            if isinstance(i, pf.Space):
                elems.pop()
            else:
                break
        return {
            'identifier': match[1+2] or match[1],
            'classes': [i[1:] or 'nonumbered' for i in match.captures(2) + match.captures(2+2)],
        }
