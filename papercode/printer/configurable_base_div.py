from papercode.printer.base_div import BaseDiv
from papercode.common.utils import UtilMethods, Paper
from papercode.language.node import Node, ClassNode, FunctionNode, CallNode, InterfaceNode, CommentNode
from papercode.printer.code_file import CodeFile
from bs4 import BeautifulSoup
import uuid

class ConfigurableBaseDiv(BaseDiv):
    def __init__(self, code_file: CodeFile):
        super().__init__(code_file)

        #Config
        self.hideBigComments = True
        self.BigCommentLimit = 6
        self.pushSmallComments = True
        self.smallCommentLimit = 2
        self.toposort = False
        self.PushCommentsInFunction = False

        # Inner Working
        # node_parition_dict = {}


    def generate_html(self, soup: BeautifulSoup, paper: Paper):
        # Given soup, Insert the main table
        # html_body = soup.find('body')
        highlight_table = self.generate_highlight_table(soup)
        partitions = []

        # Start from the root and recursively generate partitions
        root_node: Node = self.code_file.syntax_tree

        # Edge case for typescript
        if root_node.start_pos.line > 1:
            if(len(root_node.children) > 0 and root_node.children[0].start_pos.line > 1):
                end_line = min(root_node.start_pos.line - 1, root_node.children[0].start_pos.line - 1)
                part = self.code_file.get_partition(1, end_line, type(root_node))
                partitions.append({'base': part, 'node': root_node})

        partitions = self.getPartitions(root_node)
        partitions = self.squash_partitions(partitions)

        # Create partition node dict
        line_count = 0
        max_lines = paper.max_lines
        # visit_dict = {}

        for p in partitions:
            # base, side bar : create tables seperately for both
            part_length = p['base']['length']
            block_length = part_length

            # If the new partition exceeds the page limit and the page gap is not more than half the page
            if (line_count + block_length) > max_lines and (max_lines - line_count) < max_lines/2:
                # highlight_table.append(self.get_page_break_table_row(soup, max_lines - line_count - 1))
                highlight_table = self.generate_highlight_table(soup)
                line_count = 0
            table_row = self.get_table_row_from_partition(soup, p)
            highlight_table.append(table_row)
            line_count += part_length
            print('line_count: ', line_count)
            print(p['base']['line_nos'])
            line_count = line_count % (max_lines + 3)
            # Todo: Write code for page counter
            # If the line count is greater than max_length then increment the page counter and set line count to zero

    def generate_highlight_table(self, soup: BeautifulSoup):
        html_body = soup.find('body')
        table = soup.new_tag('table')
        table['class'] = ['highlighttable']
        html_body.append(table)
        return table


    def get_page_break_table_row(self, soup: BeautifulSoup, remaining_lines):
        # page_break_p = '<tr style="page-break-after: always"></tr>'
        # empty_str = '<pre>' + '\n'.join('' for i in range(remaining_lines)) + '<p style="page-break-before: always"></p>' + '</pre>'
        empty_str = '<pre>' + '\n'.join('' for i in range(remaining_lines)) + '</pre>'
        
        # Generating the line no div
        line_no_div = soup.new_tag('div')
        line_no_div['class'] = ['linenodiv']
        line_no_div.append(BeautifulSoup(empty_str, 'html.parser'))
        
        # Generating the line no td
        line_table_data = soup.new_tag('td')
        line_table_data['class'] = ['linenos']
        line_table_data.append(line_no_div)

        # Generating the code highlight div
        highlight_div = soup.new_tag('div')
        highlight_div['class'] = ['highlight']
        highlight_div.append(BeautifulSoup(empty_str, 'html.parser'))

        # Generating the code td
        code_table_data = soup.new_tag('td')
        code_table_data['class'] = ['code']
        code_table_data.append(highlight_div)

        # Sidebar td
        sidebar_table_data = soup.new_tag('td')

        table_row = soup.new_tag('tr')
        table_row['style'] = ['page-break-before: always']
        table_row.append(line_table_data)
        table_row.append(code_table_data)
        table_row.append(sidebar_table_data)

        return table_row

    def get_table_row_from_partition(self, soup: BeautifulSoup, part: dict):
        # Making the base
            base_part = part['base']
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
            if part['node'] not in self.elements_line_td:
                self.elements_line_td[part['node']] = part_uuid + '-line'
                line_table_data['id'] = self.elements_line_td[part['node']]
            line_table_data['class'] = ['linenos']
            line_table_data.append(line_no_div)

            # Generating the code highlight div
            highlight_div = soup.new_tag('div')
            highlight_div['class'] = ['highlight']
            highlight_div.append(BeautifulSoup(code_base, 'html.parser'))

            # Generating the code td
            code_table_data = soup.new_tag('td')
            if part['node'] not in self.elements_code_td:
                self.elements_code_td[part['node']] = part_uuid + '-code'
                code_table_data['id'] = self.elements_code_td[part['node']]
            code_table_data['class'] = ['code']
            code_table_data.append(highlight_div)

            # Generating the side bar table
            sidebar_table_data = soup.new_tag('td')
            if part['node'] not in self.elements_sidebar_td:
                self.elements_sidebar_td[part['node']] = part_uuid + '-sidebar'
                sidebar_table_data['id'] = self.elements_sidebar_td[part['node']]
            sidebar_table_data['class'] = ['sidebar']
            if 'sidebar' in part:
                side_table = self.get_table_for_sidebar(soup, [part['sidebar']])
                sidebar_table_data.append(side_table)

            table_row = soup.new_tag('tr')
            table_row.append(line_table_data)
            table_row.append(code_table_data)
            table_row.append(sidebar_table_data)

            return table_row
    
    def getPartitions(self, node: Node):
        partitions = []
        if type(node) == Node:
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
                partitions.extend(self.getPartitions(child))
                current_line = child.end_pos.line
            if current_line < end_line:
                # print('partition (', current_line + 1, ',', end_line, ')')
                part = self.code_file.get_partition(current_line + 1 , end_line, type(node))
                partitions.append({'base': part, 'node': node})
                current_line = end_line
        elif type(node) == ClassNode:
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
                if type(child) == FunctionNode:
                    if not self.toposort:
                        partitions.extend(self.getPartitions(child))
                else:
                    partitions.extend(self.getPartitions(child))
                current_line = child.end_pos.line
            
            if self.toposort:
                for fc in node.topo_order:
                    partitions.extend(self.getPartitions(fc))
            
            if current_line < end_line:
                # print('partition (', current_line + 1, ',', end_line, ')')
                part = self.code_file.get_partition(current_line + 1 , end_line, type(node))
                partitions.append({'base': part, 'node': node})
                current_line = end_line
            
        elif type(node) == InterfaceNode:
            # print('func partition (', node.start_pos.line, ',', node.end_pos.line, ')')
            part = self.code_file.get_partition(node.start_pos.line, node.end_pos.line, FunctionNode)
            partitions.append({'base': part, 'node': node})
        elif type(node) == FunctionNode:
            if self.PushCommentsInFunction:
                partitions.append(self.getFunctionPartition(node))
            else:
                part = self.code_file.get_partition(node.start_pos.line, node.end_pos.line, FunctionNode)
                partitions.append({'base': part, 'node': node})
        elif type(node) == CallNode:
            pass
        elif type(node) == CommentNode:
            partitions.append(self.getCommentPartition(node))
        return partitions
    
    def getFunctionPartition(self, node: FunctionNode):
        # Print evenrything except the children
        line_nos = []
        source_code_lines = []
        sidebar_line_nos = []
        sidebar_code = []
        current_line = node.start_pos.line - 1
        end_line = min(node.end_pos.line, len(self.code_file.all_lines))
        children = node.children
        for child in children:
            # Adding intermediate lines
            if current_line < child.start_pos.line - 1:
                # Add a new partition
                # print('partition (', current_line + 1, ',', child.start_pos.line - 1, '):', child.start_pos.line)
                part = self.code_file.get_partition(current_line + 1, child.start_pos.line - 1, type(node))
                line_nos.extend(part['line_nos'])
                source_code_lines.extend(part['source_code_lines'])
            
            # Add the comment partition
            commentPart = self.getCommentPartition(child)
            if 'base' in commentPart:
                line_nos.extend(commentPart['base']['line_nos'])
                source_code_lines.extend(commentPart['base']['source_code_lines'])
            else:
                remaining_lines = len(line_nos) - len(sidebar_line_nos)
                if remaining_lines > 0:
                    sidebar_line_nos.extend([' ' for i in range(remaining_lines)])
                    sidebar_code.extend([' ' for i in range(remaining_lines)])
                # adding to sidebar
                sidebar_line_nos.extend(commentPart['sidebar']['line_nos'])
                sidebar_code.extend(commentPart['sidebar']['source_code_lines'])

            current_line = child.end_pos.line
        if current_line < end_line:
            # print('partition (', current_line + 1, ',', end_line, ')')
            part = self.code_file.get_partition(current_line + 1 , end_line, type(node))
            line_nos.extend(part['line_nos'])
            source_code_lines.extend(part['source_code_lines'])
            current_line = end_line
        
        sidebar_part = {
            'line_nos': sidebar_line_nos, 
            'source_code_lines': sidebar_code, 
            'length': len(sidebar_line_nos), 
            'partition_type': CommentNode
            }
        
        base_part = {
            'line_nos': line_nos, 
            'source_code_lines': source_code_lines, 
            'length': max(len(line_nos), len(sidebar_line_nos)), 
            'partition_type': FunctionNode
            }

        return {'base': base_part, 'node': node, 'sidebar': sidebar_part}

    def getCommentPartition(self, node: CommentNode):
        if self.hideBigComments and node.size > self.BigCommentLimit:
            part = self.code_file.get_hidden_comment_node(node.start_pos.line, node.end_pos.line, '// ** LARGE COMMENT HIDDEN **', CommentNode)
            return {'base': part, 'node': node}
        elif self.pushSmallComments and node.size <= self.smallCommentLimit:
            part = self.code_file.get_partition(node.start_pos.line, node.end_pos.line, CommentNode)
            return {'sidebar': part, 'node': node}
        else:
            part = self.code_file.get_partition(node.start_pos.line, node.end_pos.line, CommentNode)
            return {'base': part, 'node': node}

    def squash_partitions(self, partitions: list):
        res_partition = []
        sidebar = {}
        for part in partitions:
            if 'base' in part:
                if sidebar:
                    if sidebar['sidebar']['length'] > part['base']['length']:
                        res_partition.append({'base': sidebar['sidebar'], 'node': sidebar['node']})
                        sidebar = {}
                    else:
                        part['sidebar'] = sidebar['sidebar']
                        sidebar = {}
                res_partition.append(part)
            elif 'sidebar' in part:
                sidebar = part
        
        if (sidebar):
            res_partition.append({'base': sidebar['sidebar'], 'node': sidebar['node']})
        return res_partition
    
    def get_table_for_sidebar(self, soup, partitions):
        side_table = soup.new_tag('table')
        for p in partitions:
            _, pcode = UtilMethods.get_pre_formated_text(p, self.code_file.language)
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
