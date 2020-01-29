from Utils import *
from bs4 import BeautifulSoup
from CodeFile import CodeFile

class CodePrinter:
    def __init__(self, pdf_file_path: str, code_file: CodeFile):
        self.pdf_file_path = pdf_file_path
        self.code_file = code_file

class RegularCodePrinter(CodePrinter):
    def __init__(self, pdf_file_path: str, code_file: CodeFile):
        super().__init__(pdf_file_path, code_file)
        self.html_template_path = 'src/templates/template2.html'
    
    def get_pre_formated_text(self, partition):
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

    def get_html_from_partitions(self):
        # todo: paper options
        template_text = text_from_file(self.html_template_path)
        soup = BeautifulSoup(template_text, 'html.parser')
        highlight_table = soup.find('table', {'class': 'highlighttable'})
        partitions = self.code_file.generate_partitions()
        for p in partitions:
            _, code_p = self.get_pre_formated_text(p)
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

    def print_code_file(self):
        html_code = self.get_html_from_partitions()
        get_pdf_sync(html_code, self.pdf_file_path)
        return html_code