from papercode.common.utils import UtilMethods
from papercode.language.node import Node, ClassNode, FunctionNode, CallNode, InterfaceNode, CommentNode
from papercode.printer.code_file import CodeFile
from bs4 import BeautifulSoup
import uuid

class BaseDiv:
    def __init__(self, code_file: CodeFile):
        self.code_file = code_file
        self.elements_line_td = {}
        self.elements_code_td = {}
        self.elements_sidebar_td = {}
    
    def generate_html(self, soup: BeautifulSoup):
        pass

class EverythingBaseDiv(BaseDiv):
    def __init__(self, code_file: CodeFile):
        super().__init__(code_file)
        self.elements_line_td = {}
        self.elements_code_td = {}
        self.elements_sidebar_td = {}
    
    def generate_html(self, soup: BeautifulSoup):
        # Given soup, Insert the main table
        highlight_table = soup.find('table', {'class': 'highlighttable'})
        partitions = []

        # Start from the root and recursively generate partitions
        root_node: Node = self.code_file.syntax_tree

        # Edge case for typescript
        if root_node.start_pos.line > 1:
            part = self.code_file.get_partition(1, root_node.start_pos.line - 1, type(root_node))
            partitions.append({'base': part, 'node': root_node})

        self.getPartitions(root_node, partitions)
        for p in partitions:
            # base, side bar : create tables seperately for both

            # Making the base
            base_part = p['base']
            part_uuid = uuid.uuid4().hex
            _, code_base = UtilMethods.get_pre_formated_text(base_part, self.code_file.language)
            # code_base = code_base.splitlines()[:base_part['length']]
            # code_base = '\n'.join(code_base)
            line_str = '<pre>' + '\n'.join(str(lno) for lno in base_part['line_nos']) + '</pre>'
            
            # Generating the line no div
            line_no_div = soup.new_tag('div')
            line_no_div['class'] = ['linenodiv']
            line_no_div.append(BeautifulSoup(line_str, 'html.parser'))
            
            # Generating the line no td
            line_table_data = soup.new_tag('td')
            if p['node'] not in self.elements_line_td:
                self.elements_line_td[p['node']] = part_uuid + '-line'
                line_table_data['id'] = self.elements_line_td[p['node']]
            line_table_data['class'] = ['linenos']
            line_table_data.append(line_no_div)

            # Generating the code highlight div
            highlight_div = soup.new_tag('div')
            highlight_div['class'] = ['highlight']
            highlight_div.append(BeautifulSoup(code_base, 'html.parser'))

            # Generating the code td
            code_table_data = soup.new_tag('td')
            if p['node'] not in self.elements_code_td:
                self.elements_code_td[p['node']] = part_uuid + '-code'
                code_table_data['id'] = self.elements_code_td[p['node']]
            code_table_data['class'] = ['code']
            code_table_data.append(highlight_div)

            # Generating the side bar table
            # side_table = self.get_table_for_sidebar(soup, p['sidebar'])
            sidebar_table_data = soup.new_tag('td')
            if p['node'] not in self.elements_sidebar_td:
                self.elements_sidebar_td[p['node']] = part_uuid + '-sidebar'
                sidebar_table_data['id'] = self.elements_sidebar_td[p['node']]
            sidebar_table_data['class'] = ['sidebar']
            # sidebar_table_data.append(side_table)

            table_row = soup.new_tag('tr')
            table_row.append(line_table_data)
            table_row.append(code_table_data)
            table_row.append(sidebar_table_data)

            highlight_table.append(table_row)

    
    def getPartitions(self, node: Node, partitions: list):
        if type(node) == Node or type(node) == ClassNode:
            # Print evenrything except the children
            current_line = node.start_pos.line - 1
            end_line = min(node.end_pos.line, len(self.code_file.all_lines))
            children = node.children
            for child in children:
                # Adding intermediate lines
                if current_line < child.start_pos.line - 1:
                    # Add a new partition
                    # print('partition (', current_line + 1, ',', child.start_pos.line - 1, '):', child.start_pos.line)
                    part = self.code_file.get_partition(current_line + 1, child.start_pos.line - 1, type(node))
                    partitions.append({'base': part, 'node': node})
                
                # Add the children partition
                self.getPartitions(child, partitions)
                current_line = child.end_pos.line
            if current_line < end_line:
                # print('partition (', current_line + 1, ',', end_line, ')')
                part = self.code_file.get_partition(current_line + 1 , end_line, type(node))
                partitions.append({'base': part, 'node': node})
                current_line = end_line
        elif type(node) == FunctionNode or type(node) == InterfaceNode:
            # print('func partition (', node.start_pos.line, ',', node.end_pos.line, ')')
            part = self.code_file.get_partition(node.start_pos.line, node.end_pos.line, FunctionNode)
            partitions.append({'base': part, 'node': node})
        elif type(node) == CallNode:
            pass
        elif type(node) == CommentNode:
            part = self.code_file.get_partition(node.start_pos.line, node.end_pos.line, CommentNode)
            partitions.append({'base': part, 'node': node})
        return

    def generate_html2(self, soup: BeautifulSoup):
        # Given soup, Insert the main table
        highlight_table = soup.find('table', {'class': 'highlighttable'})
        partitions = []

        # Parition for the initial module
        part  = self.code_file.get_partition_from_node(self.code_file.syntax_tree)
        partitions.append({'base': part, 'node': self.code_file.syntax_tree})

        # Todo what if there are functions before the node?
        for cnode in self.code_file.syntax_tree.children:
            if type(cnode) is Node:
                part  = self.code_file.get_partition_from_node(cnode)
                partitions.append({'base': part, 'node': cnode})
                continue
            elif type(cnode) is FunctionNode:
                part  = self.code_file.get_partition_from_node(cnode)
                partitions.append({'base': part, 'node': cnode})
                continue
            elif type(cnode) is ClassNode:
                part  = self.code_file.get_partition_from_node(cnode)
                partitions.append({'base': part, 'node': cnode})
                # for each function, do something
                functions = [n for n in cnode.children if type(n) is FunctionNode]

                # go through all the bif functions
                for bf in functions:
                    bf_part = self.code_file.get_partition_from_node(bf)
                    partitions.append({'base': bf_part, 'node': bf})

        for p in partitions:
            # base, side bar : create tables seperately for both

            # Making the base
            base_part = p['base']
            part_uuid = uuid.uuid4().hex
            _, code_base = UtilMethods.get_pre_formated_text(base_part, self.code_file.language)
            code_base = code_base.splitlines()[:base_part['length']]
            code_base = '\n'.join(code_base)
            line_str = '<pre>' + '\n'.join(str(lno) for lno in base_part['line_nos']) + '</pre>'
            
            # Generating the line no div
            line_no_div = soup.new_tag('div')
            line_no_div['class'] = ['linenodiv']
            line_no_div.append(BeautifulSoup(line_str, 'html.parser'))
            
            # Generating the line no td
            line_table_data = soup.new_tag('td')
            self.elements_line_td[p['node']] = part_uuid + '-line'
            line_table_data['id'] = self.elements_line_td[p['node']]
            line_table_data['class'] = ['linenos']
            line_table_data.append(line_no_div)

            # Generating the code highlight div
            highlight_div = soup.new_tag('div')
            highlight_div['class'] = ['highlight']
            highlight_div.append(BeautifulSoup(code_base, 'html.parser'))

            # Generating the code td
            code_table_data = soup.new_tag('td')
            self.elements_code_td[p['node']] = part_uuid + '-code'
            code_table_data['id'] = self.elements_code_td[p['node']]
            code_table_data['class'] = ['code']
            code_table_data.append(highlight_div)

            # Generating the side bar table
            # side_table = self.get_table_for_sidebar(soup, p['sidebar'])
            sidebar_table_data = soup.new_tag('td')
            self.elements_sidebar_td[p['node']] = part_uuid + '-sidebar'
            sidebar_table_data['id'] = self.elements_sidebar_td[p['node']]
            sidebar_table_data['class'] = ['sidebar']
            # sidebar_table_data.append(side_table)

            table_row = soup.new_tag('tr')
            table_row.append(line_table_data)
            table_row.append(code_table_data)
            table_row.append(sidebar_table_data)

            highlight_table.append(table_row)

class EmptyBaseDiv(BaseDiv):
    def __init__(self, code_file: CodeFile):
        super().__init__(code_file)
        self.elements_line_td = {}
        self.elements_code_td = {}
        self.elements_sidebar_td = {}
    
    def generate_html(self, soup: BeautifulSoup):
        # Given soup, Insert the main table
        highlight_table = soup.find('table', {'class': 'highlighttable'})
        partitions = []

        # Parition for the initial module
        part  = self.code_file.get_partition_from_node(self.code_file.syntax_tree)
        partitions.append({'base': part, 'node': self.code_file.syntax_tree})

        # Todo what if there are functions before the node?
        for cnode in self.code_file.syntax_tree.children:
            if type(cnode) is Node:
                part  = self.code_file.get_partition_from_node(cnode)
                partitions.append({'base': part, 'node': cnode})
                continue
            elif type(cnode) is FunctionNode:
                part  = self.code_file.get_partition_from_node(cnode)
                partitions.append({'base': part, 'node': cnode})
                continue
            elif type(cnode) is ClassNode:
                part  = self.code_file.get_partition_from_node(cnode)
                partitions.append({'base': part, 'node': cnode})
                # for each function, do something
                functions = [n for n in cnode.children if type(n) is FunctionNode]

                # go through all the bif functions
                for bf in functions:
                    bf_part = self.code_file.get_partition_from_node(bf)
                    partitions.append({'base': bf_part, 'node': bf})

        for p in partitions:
            # base, side bar : create tables seperately for both

            # Making the base
            base_part = p['base']
            part_uuid = uuid.uuid4().hex
            _, code_base = UtilMethods.get_pre_formated_text(base_part, self.code_file.language)
            code_base = '\n'.join(['' for i in range(base_part['length'])])
            line_str = '<pre>' + '\n'.join(str(lno) for lno in base_part['line_nos']) + '</pre>'
            
            # Generating the line no div
            line_no_div = soup.new_tag('div')
            line_no_div['class'] = ['linenodiv']
            line_no_div.append(BeautifulSoup(line_str, 'html.parser'))
            
            # Generating the line no td
            line_table_data = soup.new_tag('td')
            self.elements_line_td[p['node']] = part_uuid + '-line'
            line_table_data['id'] = self.elements_line_td[p['node']]
            line_table_data['class'] = ['linenos']
            line_table_data.append(line_no_div)

            # Generating the code highlight div
            highlight_div = soup.new_tag('div')
            highlight_div['class'] = ['highlight']
            highlight_div.append(BeautifulSoup(code_base, 'html.parser'))

            # Generating the code td
            code_table_data = soup.new_tag('td')
            self.elements_code_td[p['node']] = part_uuid + '-code'
            code_table_data['id'] = self.elements_code_td[p['node']]
            code_table_data['class'] = ['code']
            code_table_data.append(highlight_div)

            # Generating the side bar table
            # side_table = self.get_table_for_sidebar(soup, p['sidebar'])
            sidebar_table_data = soup.new_tag('td')
            self.elements_sidebar_td[p['node']] = part_uuid + '-sidebar'
            sidebar_table_data['id'] = self.elements_sidebar_td[p['node']]
            sidebar_table_data['class'] = ['sidebar']
            # sidebar_table_data.append(side_table)

            table_row = soup.new_tag('tr')
            table_row.append(line_table_data)
            table_row.append(code_table_data)
            table_row.append(sidebar_table_data)

            highlight_table.append(table_row)

class BigFunctionBaseDiv(BaseDiv):
    def __init__(self, code_file: CodeFile):
        super().__init__(code_file)
        self.elements_line_td = {}
        self.elements_code_td = {}
        self.elements_sidebar_td = {}
        self.size_limit = 3
    
    def generate_html(self, soup: BeautifulSoup):
        # Given soup, Insert the main table
        highlight_table = soup.find('table', {'class': 'highlighttable'})
        partitions = []

        # Parition for the initial module
        part  = self.code_file.get_partition_from_node(self.code_file.syntax_tree)
        partitions.append({'base': part, 'node': self.code_file.syntax_tree})

        # Todo what if there are functions before the node?
        for cnode in self.code_file.syntax_tree.children:
            if type(cnode) is Node:
                part  = self.code_file.get_partition_from_node(cnode)
                partitions.append({'base': part, 'node': cnode})
                continue
            elif type(cnode) is FunctionNode:
                part  = self.code_file.get_partition_from_node(cnode)
                partitions.append({'base': part, 'node': cnode})
                continue
            elif type(cnode) is ClassNode:
                part  = self.code_file.get_partition_from_node(cnode)
                partitions.append({'base': part, 'node': cnode})
                # for each function, do something
                functions = [n for n in cnode.children if type(n) is FunctionNode]
                big_function = [f for f in functions if f.size > self.size_limit]

                # go through all the bif functions
                for bf in big_function:
                    bf_part = self.code_file.get_partition_from_node(bf)
                    partitions.append({'base': bf_part, 'node': bf})

        for p in partitions:
            # base, side bar : create tables seperately for both

            # Making the base
            base_part = p['base']
            part_uuid = uuid.uuid4().hex
            _, code_base = UtilMethods.get_pre_formated_text(base_part, self.code_file.language)
            code_base = code_base.splitlines()[:base_part['length']]
            code_base = '\n'.join(code_base)
            line_str = '<pre>' + '\n'.join(str(lno) for lno in base_part['line_nos']) + '</pre>'
            
            # Generating the line no div
            line_no_div = soup.new_tag('div')
            line_no_div['class'] = ['linenodiv']
            line_no_div.append(BeautifulSoup(line_str, 'html.parser'))
            
            # Generating the line no td
            line_table_data = soup.new_tag('td')
            self.elements_line_td[p['node']] = part_uuid + '-line'
            line_table_data['id'] = self.elements_line_td[p['node']]
            line_table_data['class'] = ['linenos']
            line_table_data.append(line_no_div)

            # Generating the code highlight div
            highlight_div = soup.new_tag('div')
            highlight_div['class'] = ['highlight']
            highlight_div.append(BeautifulSoup(code_base, 'html.parser'))

            # Generating the code td
            code_table_data = soup.new_tag('td')
            self.elements_code_td[p['node']] = part_uuid + '-code'
            code_table_data['id'] = self.elements_code_td[p['node']]
            code_table_data['class'] = ['code']
            code_table_data.append(highlight_div)

            # Generating the side bar table
            # side_table = self.get_table_for_sidebar(soup, p['sidebar'])
            sidebar_table_data = soup.new_tag('td')
            self.elements_sidebar_td[p['node']] = part_uuid + '-sidebar'
            sidebar_table_data['id'] = self.elements_sidebar_td[p['node']]
            sidebar_table_data['class'] = ['sidebar']
            # sidebar_table_data.append(side_table)

            table_row = soup.new_tag('tr')
            table_row.append(line_table_data)
            table_row.append(code_table_data)
            table_row.append(sidebar_table_data)

            highlight_table.append(table_row)