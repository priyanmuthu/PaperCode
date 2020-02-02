from Utils import *
from bs4 import BeautifulSoup
from CodeFile import CodeFile
from CodePrinter import CodePrinter
from language import Node

class SidebarCodePrinter(CodePrinter):
    def __init__(self, pdf_file_path: str, code_file: CodeFile):
        super().__init__(pdf_file_path, code_file)
        self.html_template_path = 'src/templates/sidebar.html'
        self.size_limit = 3
    
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

    def get_html(self):
        # todo: paper options
        # start with the syntax tree
        template_text = text_from_file(self.html_template_path)
        soup = BeautifulSoup(template_text, 'html.parser')
        highlight_table = soup.find('table', {'class': 'highlighttable'})
        flat_tree = []
        flatten_syntax_tree(self.code_file.syntax_tree, [Node.FunctionNode, Node.CallNode], flat_tree)
        partitions = []

        # Parition for the initial module
        part  = self.code_file.get_partition_from_node(self.code_file.syntax_tree)
        partitions.append({'base': part, 'sidebar': []})

        # Todo what if there are functions before the node?
        for node in self.code_file.syntax_tree.children:
            if type(node) is Node.Node:
                part  = self.code_file.get_partition_from_node(node)
                partitions.append({'base': part, 'sidebar': []})
                continue
            elif type(node) is Node.FunctionNode:
                part  = self.code_file.get_partition_from_node(node)
                partitions.append({'base': part, 'sidebar': []})
                continue
            elif type(node) is Node.ClassNode:
                part  = self.code_file.get_partition_from_node(node)
                partitions.append({'base': part, 'sidebar': []})
                # for each function, do something
                functions = [n for n in node.children if type(n) is Node.FunctionNode]

                big_funcs = [f for f in functions if f.size > self.size_limit]
                small_funcs = {f: False for f in functions if f.size <= self.size_limit}

                # go through all the bif functions
                for bf in big_funcs:
                    bf_part = {
                        'base': self.code_file.get_partition_from_node(bf),
                        'sidebar': []
                        }
                    filled_size = 0
                    for fc in bf.function_calls:
                        f_node = fc.function_node
                        if f_node is None:
                            continue
                        if f_node in small_funcs and (not small_funcs[f_node]) and (filled_size+f_node.size) < bf.size:
                            bf_part['sidebar'].append(self.code_file.get_partition_from_node(f_node))
                            filled_size += f_node.size + 1
                            small_funcs[f_node] = True
                    
                    partitions.append(bf_part)
                
                for sf in small_funcs.keys():
                    if small_funcs[sf]:
                        continue
                    sf_part = {
                        'base': self.code_file.get_partition_from_node(sf),
                        'sidebar': []
                        }
                    partitions.append(sf_part)

        for p in partitions:
            # base, side bar : create tables seperately for both

            # Making the base
            base_part = p['base']
            _, code_base = self.get_pre_formated_text(base_part)
            code_base = code_base.splitlines()[:base_part['length']]
            code_base = '\n'.join(code_base)
            line_str = '<pre>' + '\n'.join(str(lno) for lno in base_part['line_nos']) + '</pre>'
            
            # Generating the line no div
            line_no_div = soup.new_tag('div')
            line_no_div['class'] = ['linenodiv']
            line_no_div.append(BeautifulSoup(line_str, 'html.parser'))
            
            # Generating the line no td
            line_table_data = soup.new_tag('td')
            line_table_data['class'] = ['linenos']
            line_table_data.append(line_no_div)

            # Generating the code highlight div
            highlight_div = soup.new_tag('div')
            highlight_div['class'] = ['highlight']
            highlight_div.append(BeautifulSoup(code_base, 'html.parser'))

            # Generating the code td
            code_table_data = soup.new_tag('td')
            code_table_data['class'] = ['code']
            code_table_data.append(highlight_div)

            # Generating the side bar table
            side_table = self.get_table_for_sidebar(soup, p['sidebar'])
            sidebar_table_data = soup.new_tag('td')
            sidebar_table_data['class'] = ['sidebar']
            sidebar_table_data.append(side_table)

            table_row = soup.new_tag('tr')
            table_row.append(line_table_data)
            table_row.append(code_table_data)
            table_row.append(sidebar_table_data)

            highlight_table.append(table_row)
            
        return str(soup)

    def get_table_for_sidebar(self, soup, partitions):
        side_table = soup.new_tag('table')
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

            side_table.append(table_row)
        return side_table

    def print_code_file(self):
        html_code = self.get_html()
        get_pdf_sync(html_code, self.pdf_file_path)
        return html_code
