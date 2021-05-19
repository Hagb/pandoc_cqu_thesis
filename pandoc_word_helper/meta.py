import panflute as pf


class Meta:
    codeBlockNumbering = True  # 对代码块添加行号
    codeBlockNumberingMinLine = 3  # 显示行号的最小代码块行数（最小0）
    codeSpaceVisible = False  # 显示代码中的空格

    chapters = True  # 编号chapter.item
    chaptersDepth = 1  # 标题编号深度，默认只有一级标题编号
    autoEqnLabels = True  # 自动公式编号
    tableEqns = True  # 用表格编号公式，在预览时有效

    figureTitle = "图 "
    figureTitle2 = "Figure "
    tableTitle = "表"
    tableTitle2 = "Table "
    titleDelim = ' '  # 题注编号和题注文本直接的分隔符

    # 引用编号时的参数
    figPrefix = "图"
    eqnPrefix = "式"
    tblPrefix = "表"
    secPrefix = "节"
    chapDelim = '.'  # 编号chapter.item中间的“点”

    def __init__(self, doc: pf.Doc):
        metadata = doc.get_metadata()
        for name in metadata:
            data = type(getattr(self, name))(metadata[name]) if hasattr(
                self, name) else metadata[name]
            setattr(self, name, data)
