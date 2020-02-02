from papercode.language.Highlighter import Highlighter
from pyppeteer import launch
from PyPDF2 import PdfFileWriter, PdfFileReader
from bs4 import BeautifulSoup
import asyncio
import sys

class PaperOptions:
    def __init__(self, paper_size, max_lines):
        self.paper_size = paper_size
        self.max_lines = max_lines

print_paper = {
    'A4': PaperOptions('A4', 96)
}

class UtilMethods:

    @staticmethod
    def text_from_file(file_path):
        f = open(file_path, 'r')
        file_text = f.read()
        f.close()
        return file_text

    @staticmethod
    def highlight(source_code):
        highlighter = Highlighter()
        return highlighter.highlight_python_file(source_code)

    @staticmethod
    def flatten_syntax_tree(tree_node, filter_types = [], flat_tree = []):
        if(type(tree_node) not in filter_types):
            flat_tree.append(tree_node)
        
        for child in tree_node.children:
            UtilMethods.flatten_syntax_tree(child, filter_types, flat_tree)

    @staticmethod
    def print_syntax_tree(tree_node):
        tree_node.print()
        for child in tree_node.children:
            UtilMethods.print_syntax_tree(child)

    @staticmethod
    def isBlank (myString):
        return not (myString and myString.strip())

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def get_pdf_sync(html_code, pdf_file_path):
        asyncio.get_event_loop().run_until_complete(UtilMethods.get_pdf(html_code, pdf_file_path))

    @staticmethod
    def get_pre_formated_text(partition):
        partition_code = '\n'.join(partition['source_code_lines'])
        partition_html = UtilMethods.highlight(partition_code)
        soup = BeautifulSoup(partition_html, 'html.parser')
        res = soup.find('table')
        td_line_nos = res.find('td')
        td_code = td_line_nos.find_next_sibling()
        code_preformated_text = td_code.find('pre')
        #generating line_preformated_text
        line_soup = soup.new_tag('pre')
        line_soup.string = '' + '\n'.join(str(lno) for lno in partition['line_nos'])
        return line_soup, str(code_preformated_text)