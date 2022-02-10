import regex
import panflute as pf
_attr_regex = r'(?:#([^ \{\}]+)|(\.[^ \{\}]+|-))'
attrs_regex = r'(?:\{\s*' + f'(?:{_attr_regex}\\s+)*{_attr_regex}' + r'\s*\}|\{\s*v\})'
anchor_re = regex.compile(r'^\s*' + attrs_regex + r'\s*$')


def stripLabel(elems, tail=True, strip_inplace = True):
    label_strs = []
    for i in elems[::-1] if tail else elems:
        if isinstance(i, (pf.Space, pf.SoftBreak, pf.Str)):
            label_strs.append(pf.stringify(i))
            if tail and label_strs[-1].startswith('{'):
                break
            elif (not tail) and label_strs[-1].endswith('}'):
                break
        else:
            return
    match = anchor_re.match(
        ''.join(label_strs[::-1] if tail else label_strs))
    if match:
        strip_len = len(label_strs)
        if strip_len + 1 <= len(elems):
            if tail and isinstance(elems[-strip_len-1], (pf.Space, pf.SoftBreak)):
                strip_len += 1
            elif (not tail) and isinstance(elems[strip_len], (pf.Space, pf.SoftBreak)):
                strip_len += 1
        if strip_inplace:
            target_elems = elems[:-strip_len] if tail else elems[strip_len:]
            elems.clear()
            elems.extend(target_elems)
        return {
            'identifier': match[1+2] or match[1] or '',
            'classes': [i[1:] or 'unnumbered' for i in match.captures(2) + match.captures(2+2)],
            'strip_len': strip_len
        }
