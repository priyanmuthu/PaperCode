from papercode.common.Utils import UtilMethods
from papercode.printer.BaseDiv import BaseDiv, EverythingBaseDiv
from papercode.language import Node
from papercode.printer.CodeFile import CodeFile
from bs4 import BeautifulSoup
import uuid

class SidebarDiv:
    def __init__(self, base_div: BaseDiv, code_file: CodeFile):
        self.code_file = code_file
        self.base_div = base_div
    
    def generate_html(self, soup: BeautifulSoup):
        pass

class SmallFunctionSidebarDiv(SidebarDiv):
    def __init__(self, base_div: BaseDiv, code_file: CodeFile, size_limit: int):
        if not(type(base_div) is EverythingBaseDiv):
            raise Exception('Unsupported Sidebar')
        super().__init__(base_div, code_file)
        self.size_limit = size_limit

    def generate_html(self, soup: BeautifulSoup):
        # Check sidebar compatibility
        if not(type(self.base_div) is EverythingBaseDiv):
            return
        # Get all the small functions and add beside the big functions
        sidebar_dict = {}
        for node in self.code_file.syntax_tree.children:
            if type(node) is Node.Node:
                continue
            elif type(node) is Node.FunctionNode:
                continue
            elif type(node) is Node.ClassNode:
                # for each function, do something
                functions = [n for n in node.children if type(n) is Node.FunctionNode]

                big_funcs = [f for f in functions if f.size > self.size_limit]

                # go through all the bif functions
                for bf in big_funcs:
                    sidebar = []
                    filled_size = 0
                    small_funcs = {f: False for f in functions if f.size <= self.size_limit}
                    for fc in bf.function_calls:
                        f_node = fc.function_node
                        if f_node is None:
                            continue
                        if f_node in small_funcs and (not small_funcs[f_node]) and (filled_size+f_node.size) < bf.size:
                            sidebar.append(self.code_file.get_partition_from_node(f_node))
                            filled_size += f_node.size + 1
                            small_funcs[f_node] = True
                    
                    # to big functions part
                    sidebar_dict[bf] = sidebar
                

        for bf in sidebar_dict.keys():
            if bf not in self.base_div.elements_sidebar_td:
                continue
            bf_uuid = self.base_div.elements_sidebar_td[bf]
            sidebar_td = soup.find('td', {'id': bf_uuid})
            sidebar_td.append(self.get_table_for_sidebar(soup, sidebar_dict[bf]))
    
    def get_table_for_sidebar(self, soup, partitions):
        side_table = soup.new_tag('table')
        for p in partitions:
            _, code_p = UtilMethods.get_pre_formated_text(p)
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
