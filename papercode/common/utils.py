from papercode.language.highlighter import Highlighter
from pyppeteer import launch
from PyPDF2 import PdfFileWriter, PdfFileReader
from bs4 import BeautifulSoup
import asyncio
import sys
import os.path
import enum
import qrcode
from io import BytesIO
import base64

class Language(enum.Enum):
    Python = 1
    Typescript = 2
    R = 3

class Paper:
    def __init__(self, paper_size, max_lines, template_path):
        self.paper_size = paper_size
        self.max_lines = max_lines
        self.template_path = template_path

print_paper = {
    'A4P': Paper('A4', 85, 'papercode/templates/sidebar_portrait.html'),
    'A4L': Paper('A4', 50, 'papercode/templates/sidebar_landscape.html'),
}

class Position:
    def __init__(self, line: int, column: int):
        self.line = line
        self.column = column
    
    def __str__(self):
        return '(' + str(self.line) + ',' + str(self.column) + ')'

class UtilMethods:

    @staticmethod
    def text_from_file(file_path: str):
        f = open(file_path, 'r')
        file_text = f.read()
        f.close()
        return file_text
    
    @staticmethod
    def write_text_to_file(file_path: str, text: str):
        file = open(file_path, 'w')
        file.write(text)
        file.close()

    @staticmethod
    def get_file_ext(file_path: str):
        return os.path.splitext(file_path)[-1]

    @staticmethod
    def highlight(source_code: str, lang: Language = Language.Python):
        highlighter = Highlighter()
        if lang == Language.Python:
            return highlighter.highlight_python_file(source_code)
        elif lang == Language.Typescript:
            return highlighter.highlight_ts_file(source_code)
        elif lang == Language.R:
            return highlighter.highlight_r_file(source_code)
        else:
            return highlighter.highlight_file(source_code)

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
            'displayHeaderFooter': False,
            'scale': 0.8,
            'margin': { 'top': "2cm", 'bottom': "1cm", 'left': "1cm", 'right': "1cm" },
        })
        # 'headerTemplate': '<header style="margin: auto; width: 40%"><img style="float: right; marginTop: 30px; marginRight: 20px; marginLeft: 8px; width: 25%; z-index: 10;" src="data:image/png;base64, iVBORw0KGgoAAAANSUhEUgAAAH0AAAB9AQAAAACn+1GIAAABI0lEQVR4nK2UMWrDQBRE3/cK1p18g/VJJHIvgRSce+QokfBFVgcIbDoJZE0KFYGQyvm/nOLBnxkGgBR3SBoBTvy6Z4QobayhACbJB8pkA/q4AHzZ1QkKgGmY/8v4uepgUn+++0GJ0pbiXg8pTm6ermYV3OcNZGY+UEnK6AJLK2lxgdqJ1+v6ogozG+azV/phWiBMUFdeQe10SXutDJB8oEDIS6tbjpNuPp6inS7REORXKTQSMm3ps8Za2el9KxBVgFaDk6faCZmGDhqCk6c09YakIQF99im/phJ0hsOD5FJ+ANJCLcWp9E6DEqWNs5W3mQZmz+V/2MBql2cZfwv30rG05XH1ST+OdIm2QNwJTuU/ln+kS3Gkd9rTY/lbVWCqcKnUN41SkTzCxZb8AAAAAElFTkSuQmCC" alt="Pivohub" /></header>'
        await browser.close()

    @staticmethod
    def get_pdf_sync(html_code, pdf_file_path):
        retry_limit = 3
        attempt = 0
        while(attempt < retry_limit):
            try:
                attempt += 1
                asyncio.get_event_loop().run_until_complete(UtilMethods.get_pdf(html_code, pdf_file_path))
                break
            except Exception:
                if attempt >= retry_limit:
                    raise Exception('PDF printing maximum retry reached')

    @staticmethod
    def get_preformated_innerhtml(code: str, lang: Language = Language.Python):
        partition_html = UtilMethods.highlight(code, lang)
        soup = BeautifulSoup(partition_html, 'html.parser')
        res = soup.find('table')
        td_line_nos = res.find('td')
        td_code = td_line_nos.find_next_sibling()
        code_preformated_text = td_code.find('pre')
        code_innerhtml = code_preformated_text.decode_contents().splitlines()
        return code_innerhtml

    @staticmethod
    def get_pre_formated_text(partition, lang: Language = Language.Python):
        partition_code = '\n'.join(partition.source_code_lines)
        partition_html = UtilMethods.highlight(partition_code, lang)
        soup = BeautifulSoup(partition_html, 'html.parser')
        res = soup.find('table')
        td_line_nos = res.find('td')
        td_code = td_line_nos.find_next_sibling()
        code_preformated_text = td_code.find('pre')
        #generating line_preformated_text
        line_soup = soup.new_tag('pre')
        line_soup.string = '' + '\n'.join(str(lno) for lno in partition['line_nos'])
        return line_soup, str(code_preformated_text)
    
    @staticmethod
    def getQRCodeFromData(data: str):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=0,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8") 
        return img_str