from language import Highlighter
from language import Node
from Utils import *
from CodeFile import CodeFile
from bs4 import BeautifulSoup
from pyppeteer import launch
from PyPDF2 import PdfFileWriter, PdfFileReader
import math
import asyncio
import libcst
import sys


def highlight(source_code):
    highlighter = Highlighter.Highlighter()
    return highlighter.highlight_python_file(source_code)

def get_pre_formated_text(partition):
    partition_code = '\n'.join(partition['source_code_lines'])
    partition_html = highlight(partition_code)
    soup = BeautifulSoup(partition_html, 'html.parser')
    res = soup.find('table')
    td_line_nos = res.find('td')
    td_code = td_line_nos.find_next_sibling()
    code_preformated_text = td_code.find('pre')
    #generating line_preformated_text
    line_soup = soup.new_tag('pre')
    line_soup.string = '' + '\n'.join(str(lno) for lno in partition['line_nos'])
    return line_soup, str(code_preformated_text)

def generate_html_from_template(html_template_path, line_nos, code_lines):
    template_text = text_from_file(html_template_path)
    soup = BeautifulSoup(template_text, 'html.parser')
    line_no_div = soup.find('div', {'class': 'linenodiv'})
    highlight_div = soup.find('div', {'class': 'highlight'})
    preformatted_line = '<pre>' + '\n'.join(line_nos) + '</pre>'
    preformatted_code = '<pre>' + '\n'.join(code_lines) + '</pre>'
    line_no_div.append(BeautifulSoup(preformatted_line, 'html.parser'))
    highlight_div.append(BeautifulSoup(preformatted_code, 'html.parser'))
    return str(soup)

def get_html_from_partitions(html_template_path, source_code, partitions, paper_options):
    template_text = text_from_file(html_template_path)
    soup = BeautifulSoup(template_text, 'html.parser')
    highlight_table = soup.find('table', {'class': 'highlighttable'})
    for p in partitions:
        _, code_p = get_pre_formated_text(p)
        pcode = code_p.splitlines()[:p['length']]
        pcode = '\n'.join(pcode)
        line_str = '<pre>' + '\n'.join(str(lno) for lno in p['line_nos']) + '</pre>'
        # Generating the table row
        line_no_div = soup.new_tag('div')
        line_no_div['class'] = ['linenodiv']
        line_no_div.append(BeautifulSoup(line_str, 'html.parser'))

        line_table_data = soup.new_tag('td')
        line_table_data['class'] = ['linenos']
        line_table_data.append(line_no_div)


        highlight_div = soup.new_tag('div')
        highlight_div['class'] = ['highlight']
        highlight_div.append(BeautifulSoup(pcode, 'html.parser'))

        code_table_data = soup.new_tag('td')
        code_table_data['class'] = ['code']
        code_table_data.append(highlight_div)

        table_row = soup.new_tag('tr')
        table_row.append(line_table_data)
        table_row.append(code_table_data)

        highlight_table.append(table_row)
        
        
    return str(soup)
    

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

def main():
    file_path = 'src/temp/fpdf.py'
    template_path = 'src/template2.html'
    pdf_file_path = 'src/temp/pup.pdf'
    code_file = CodeFile(file_path)
    code_file.process()    
    partitions = code_file.generate_partitions()
    final_code = get_html_from_partitions(template_path, code_file.source_code, partitions, print_paper['A4'])
    asyncio.get_event_loop().run_until_complete(get_pdf(final_code, pdf_file_path))
    # generate_pdf_two_page_layout(pdf_file_path, 'src/temp/pup2.pdf')
    print(final_code)


if __name__ == "__main__":
    main()