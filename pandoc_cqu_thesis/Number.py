import abc
import typing
import panflute as pf


class NumberFilter(abc.ABC):
    auto_labels = True

    def getNumberingInfo(self, attr):
        if isinstance(attr, pf.Element):
            attr = {
                'identifier': getattr(attr, 'identifier', ''),
                'classes': getattr(attr, 'classes', set())
            }
        if not isinstance(attr, dict):
            attr = {}
        identifier = attr.get('identifier', '') or ''
        classes = attr.get('classes', set())
        numbering = (identifier or self.auto_labels or 'tag' in classes) and \
            ('notag' not in classes and 'unnumbered' not in classes)
        return {'identifier': identifier, 'numbering': numbering}
