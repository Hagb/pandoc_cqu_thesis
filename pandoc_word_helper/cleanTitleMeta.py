import panflute as pf

def cleanTitleMeta(doc: pf.Doc):
    for meta in ('title', 'subtitle', 'author', 'date', 'abstract'):
        if meta in doc.metadata:
            doc.metadata.content.pop(meta)

def main(doc=None, meta=None):
    return pf.run_filters([], prepare=cleanTitleMeta, doc=doc)


if __name__ == "__main__":
    main()
