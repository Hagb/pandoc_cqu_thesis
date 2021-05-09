import panflute as pf

class Meta:
    codeBlockNumbering = True # 对代码块添加行号
    codeSpaceVisible = False # 显示代码中的空格

    chapters = True # 编号chapter.item
    chaptersDepth = 2 # 标题编号深度，默认只有一级标题编号
    autoEqnLabels = True # 自动公式编号
    tableEqns = True # 用表格编号公式，在预览时有效

    figureTitle = "图片 "
    figureTitle2 = "Figure "
    tableTitle = "Table"
    titleDelim = ':' # 题注编号和题注文本直接的分隔符

    # 引用编号时的参数
    figPrefix = "图"
    eqnPrefix = "式"
    tblPrefix = "表"
    secPrefix = "节"
    chapDelim = '.' # 编号chapter.item中间的“点”
