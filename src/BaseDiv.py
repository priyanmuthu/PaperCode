from language import Node
from CodeFile import CodeFile
from bs4 import BeautifulSoup

class BaseDiv:
    def __init__(code_file: CodeFile):
        self.code_file = code_file
        self.elements = {}

class EverythingBaseDiv(BaseDiv):
    def __init__(code_file: CodeFile):
        super().__init__(code_file)
        self.elements = {}
    
    def generate_html(soup: BeautifulSoup):
        # Given soup, Insert the main table
        highlight_table = soup.find('table', {'class': 'highlighttable'})
        flat_tree = []
        flatten_syntax_tree(self.code_file.syntax_tree, [Node.FunctionNode, Node.CallNode], flat_tree)
        partitions = []

        # Parition for the initial module
        part  = self.code_file.get_partition_from_node(self.code_file.syntax_tree)
        partitions.append({'base': part, 'node': self.code_file.syntax_tree})

        # Todo what if there are functions before the node?
        for node in self.code_file.syntax_tree.children:
            if type(node) is Node.Node:
                part  = self.code_file.get_partition_from_node(node)
                partitions.append({'base': part, 'node': node})
                continue
            elif type(node) is Node.FunctionNode:
                part  = self.code_file.get_partition_from_node(node)
                partitions.append({'base': part, 'node': node})
                continue
            elif type(node) is Node.ClassNode:
                part  = self.code_file.get_partition_from_node(node)
                partitions.append({'base': part, 'node': node})
                # for each function, do something
                functions = [n for n in node.children if type(n) is Node.FunctionNode]

                # go through all the bif functions
                for bf in functions:
                    bf_part = self.code_file.get_partition_from_node(bf)
                    partitions.append({'base': bf_part, 'node': bf})

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