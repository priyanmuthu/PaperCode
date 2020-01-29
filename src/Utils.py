from language import Highlighter
from pyppeteer import launch
from PyPDF2 import PdfFileWriter, PdfFileReader
import asyncio

class PaperOptions:
    def __init__(self, paper_size, max_lines):
        self.paper_size = paper_size
        self.max_lines = max_lines

print_paper = {
    'A4': PaperOptions('A4', 96)
}

def text_from_file(file_path):
    f = open(file_path, 'r')
    file_text = f.read()
    f.close()
    return file_text

def highlight(source_code):
    highlighter = Highlighter.Highlighter()
    return highlighter.highlight_python_file(source_code)

def flatten_syntax_tree(tree_node, filter_types = [], flat_tree = []):
    if(type(tree_node) not in filter_types):
        flat_tree.append(tree_node)
    
    for child in tree_node.children:
        flatten_syntax_tree(child, filter_types, flat_tree)


def print_syntax_tree(tree_node):
    tree_node.print()
    for child in tree_node.children:
        print_syntax_tree(child)

def isBlank (myString):
    return not (myString and myString.strip())

def generate_pdf_two_page_layout(pdf_file_path, out_path):
    input1 = PdfFileReader(open(pdf_file_path, "rb"))
    output = PdfFileWriter()
    for iter in range (0, input1.getNumPages()-1, 2):
        lhs = input1.getPage(iter)
        rhs = input1.getPage(iter+1)
        lhs.mergeTranslatedPage(rhs, lhs.mediaBox.getUpperRight_x(),0, True)
        output.addPage(lhs)
        sys.stdout.flush()

    # print("writing " + sys.argv[2])
    outputStream = open(out_path, "wb")
    output.write(outputStream)

async def get_pdf(html_code, pdf_file_path):
    browser = await launch()
    page = await browser.newPage()
    await page.setContent(html_code)
    await page.pdf({
        'path': pdf_file_path,
        # 'format': 'A4',
        'preferCSSPageSize': True,
        'printBackground': True,
        # 'displayHeaderFooter': True,
        'margin': { 'top': "1cm", 'bottom': "1cm", 'left': "1cm", 'right': "1cm" }
    })
    await browser.close()

def get_pdf_sync(html_code, pdf_file_path):
    asyncio.get_event_loop().run_until_complete(get_pdf(html_code, pdf_file_path))