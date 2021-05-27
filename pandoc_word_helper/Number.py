import abc
import typing


class NumberFilter(abc.ABC):
    auto_labels = True

    def getNumberingInfo(self, attr=typing.Optional[dict]):
        if not isinstance(attr, dict):
            attr = {}
        identifier = attr.get('identifier', '') or ''
        classes = attr.get('classes', set())
        numbering = (identifier or self.auto_labels or 'tag' in classes) and \
            ('notag' not in classes and 'nonumbered' not in classes)
        return {'identifier': identifier, 'numbering': numbering}
