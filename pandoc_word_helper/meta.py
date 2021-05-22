import panflute as pf


class Meta:
    codeBlockNumbering = True  # 对代码块添加行号
    codeBlockNumberingMinLine = 3  # 显示行号的最小代码块行数（最小0）
    codeSpaceVisible = False  # 显示代码中的空格

    # 题注相关的参数
    # 将按照title chapter chapDelim item titleDelim的格式显示
    # 例如：“图 1.2.3:这是图片题注”，“1.2”为标题编号即chapter，“3”对应item，
    # 前缀“图 ”由figureTitle决定，标题编号“1.2”的深度由chapteresDepth决定
    # “1.2”与“3”中间的点由chapDelim决定
    # 题注前缀与题注文本的分隔符“:”由titleDelim决定
    # Markdown中，空格需要转义为'&#32;'
    chapDelim = '.'  # 编号chapter.item中间的“点”
    chapters = True  # 编号chapter.item
    chaptersDepth = 1  # 标题编号深度，默认只有一级标题编号
    tableEqns = True  # 用表格编号公式，在预览时有效

    figureTitle = "图 "
    figureTitle2 = "Figure "
    tableTitle = "表 "
    tableTitle2 = "Table "
    titleDelim = ' '  # 题注编号和题注文本直接的分隔符

    # 引用编号时的参数
    figPrefix = "图"
    eqnPrefix = "式"
    tblPrefix = "表"
    secPrefix = "§"
    pagePrefix = "p. "

    secondCaptionSeparator = r"\sc{}"  # 双语题注的第二题注的分隔符
    isParaAfterTable = False  # 表格之后是否自动生成空段落（CQU的格式要求）

    autoEqnLabels = True  # 自动公式编号
    # 公式编号格式为 eqPrefix chapter chapDelim item eqSuffix
    # 例如："(4.1)"
    eqPrefix = '('
    eqSuffix = ')'

    proof = "证明："
    proofQed = "□"

    theoremSeparator = '：'
    theoremPrefix = '（'
    theoremSuffix = '）'
    theorems = {'assumption': '假设',
                'axiom': '公理',
                'conjecture': '猜想',
                'corollary': '推论',
                'definition': '定义',
                'example': '例',
                'exercise': '练习',
                'lemma': '引理',
                'problem': '问题',
                'proposition': '命题',
                'remark': '注释',
                'theorem': '定理'}

    def __init__(self, doc: pf.Doc):
        metadata = doc.get_metadata()
        for name in metadata:
            data = type(getattr(self, name))(metadata[name]) if hasattr(
                self, name) else metadata[name]
            setattr(self, name, data)
