from papercode.printer.base_div import BaseDiv
from papercode.common.utils import UtilMethods, Paper
from papercode.language.node import Node, ClassNode, FunctionNode, CallNode, InterfaceNode, CommentNode
from papercode.printer.code_file import CodeFile, CodePartition
from bs4 import BeautifulSoup
from collections import defaultdict
from os.path import abspath
import difflib
import uuid
import textwrap

class PagePartition:
    def __init__(self, base: CodePartition = None, node: Node = None, sidebar: CodePartition = None):
        self.base = base
        self.node = node
        self.sidebar = sidebar

class Page:
    def __init__(self, page_no):
        self.page_line_nos = []
        self.page_lnos = []
        self.page_code_lines = []
        self.page_sidebar_line_nos = []
        self.page_sidebar_code_lines = []
        self.page_no = str(page_no)
        self.page_length = 0
        self.sidebar_line_dict = {}
        self.sidebar_code_dict = {}
        self.sidebar_wrap_dict = {}
    
    def process_sidebar(self):
        cur_line = 0
        wrapper = textwrap.TextWrapper(width=50)
        while(cur_line < self.page_length):
            if cur_line in self.sidebar_line_dict:
                line_length = self.sidebar_wrap_dict[cur_line]
                self.page_sidebar_line_nos.append(self.sidebar_line_dict[cur_line])
                self.page_sidebar_code_lines.append(self.sidebar_code_dict[cur_line])
                cur_line += line_length # Should be the wrapped line length
            else:
                self.page_sidebar_line_nos.append(' ')
                self.page_sidebar_code_lines.append(' ')
                cur_line += 1
        pass

class AuxPartition:
    def __init__(self, partition: CodePartition, line: int, page: int):
        self.partition = partition
        self.line = line
        self.page = page

class ConfigurableBaseDiv(BaseDiv):
    def __init__(self, code_file: CodeFile):
        super().__init__(code_file)

        #Config
        self.hideBigComments = True
        self.BigCommentLimit = 6
        self.pushSmallComments = True
        self.smallCommentLimit = 2
        self.toposort = True
        self.PushCommentsInFunction = True
        self.RemoveEmptyLines = True
        self.BoldFunctionStartLine = True

        # Auxiliary page with info
        self.LargeCommentsInAuxiliary = True

        # diff auxiliary page
        self.DiffInAuxiliary = True
        self.DiffFilePath = abspath('../PaperCode/papertsc/test/pytutor.ts')

        # Inner Working
        self.node_parition_dict = {}
        self.function_nodes = []
        self.node_page_dict = {}
        self.pages = {}
        self.line_page_dict = {}
        self.auxiliary_partition_dict = {}
        self.diff_auxiliary_partition_dict = {}
        self.all_pages = []
        self.code_page_line_dict = {}   # Dictionary [code line] -> [page line]




    def generate_html(self, soup: BeautifulSoup, paper: Paper):
        # Given soup, Insert the main table
        # html_body = soup.find('body')
        # highlight_table = self.generate_highlight_table(soup)
        partitions = []

        # Start from the root and recursively generate partitions
        root_node: Node = self.code_file.syntax_tree

        # Edge case for typescript
        if root_node.start_pos.line > 1:
            if(len(root_node.children) > 0 and root_node.children[0].start_pos.line > 1):
                end_line = min(root_node.start_pos.line - 1, root_node.children[0].start_pos.line - 1)
                part = self.code_file.get_partition(1, end_line, type(root_node))
                partitions.append(PagePartition(part, root_node))

        partitions = self.getPartitions(root_node)
        
        # Post process
        # Squashing comments to sidebar
        partitions = self.squash_partitions(partitions)
        # Removing empty lines
        if self.RemoveEmptyLines:
            partitions = self.remove_empty_partitions(partitions)
        # Table-of-contents
        self.pre_calculcate_pages(partitions, paper) # Pre-calculating pages
        # Todo: Fix wraping here
        partitions = self.table_of_contents(partitions)

        # Create partition node dict
        line_count = 0
        max_lines = paper.max_lines
        
        # Manual page split
        page_count = 1
        # page_metadata = {}
        current_page = Page(str(page_count))

        for p in partitions:
            part_length = p.base.length
            if (line_count + part_length) > max_lines and (max_lines - line_count) < max_lines/2:
                # Start a new page
                current_page.page_length = line_count
                self.pages[page_count] = current_page
                current_page.process_sidebar()
                page_count += 1
                line_count = 0
                current_page = Page(str(page_count))
            lnos = p.base.line_nos
            line_nos = [self.get_line_no_str(lno) for lno in p.base.line_nos]
            code_lines = p.base.format_code_lines
            sidebar_line_nos = None
            sidebar_code_lines = None
            sidebar_length = 0
            if not(p.sidebar is None):
                sidebar_line_nos = p.sidebar.line_nos
                sidebar_code_lines = p.sidebar.format_code_lines
                sidebar_length = p.sidebar.length

            if self.BoldFunctionStartLine:
                if p.base.partition_type == FunctionNode:
                    line_nos[0] = '<span class="boldlinenos">' + line_nos[0] + '</span>'

            for i in range(len(lnos)):
                line_length = self.code_file.line_wrap_length[lnos[i]]
                if (line_count + line_length) > max_lines:
                    current_page.page_length = line_count
                    current_page.process_sidebar()
                    self.pages[page_count] = current_page
                    page_count += 1
                    line_count = 0
                    current_page = Page(str(page_count))
                
                self.line_page_dict[lnos[i]] = page_count
                self.code_page_line_dict[lnos[i]] = line_count
                current_page.page_lnos.append(lnos[i])
                current_page.page_line_nos.append(line_nos[i])
                current_page.page_code_lines.append(code_lines[i])
                # Todo: wrap text modifications
                if sidebar_line_nos and sidebar_code_lines and i < sidebar_length:
                    current_page.sidebar_line_dict[line_count] = sidebar_line_nos[i]
                    current_page.sidebar_code_dict[line_count] = sidebar_code_lines[i]
                    if type(sidebar_line_nos[i]) is str:
                        current_page.sidebar_wrap_dict[line_count] = 1
                    else:
                        current_page.sidebar_wrap_dict[line_count] = self.code_file.sidebar_line_wrap_length[sidebar_line_nos[i]]

                    # current_page.page_sidebar_line_nos.append(sidebar_line_nos[i])
                    # current_page.page_sidebar_code_lines.append(sidebar_code_lines[i])
                # else:
                #     current_page.page_sidebar_line_nos.append(' ')
                #     current_page.page_sidebar_code_lines.append(' ')
                line_count += line_length

        if len(current_page.page_line_nos) > 0:
            # There is still some code left
            current_page.page_length = line_count
            self.pages[page_count] = current_page
            current_page.process_sidebar()
            page_count += 1
            line_count = 0
            current_page = Page(str(page_count))
        for page in self.pages:
            self.all_pages.append(self.pages[page])
        self.add_pages_html(soup, self.pages)
    
    def get_line_no_str(self, lno: int):
        lStr = [str(lno)]
        for i in range(self.code_file.line_wrap_length[lno] - 1):
            lStr.append("*")
        return '\n'.join(lStr)

    def add_pages_html(self, soup: BeautifulSoup, pages: dict):
        # Generate a table for each page
        for page in pages:
            # highlight_table = self.generate_highlight_table(soup)
            highlight_table, sidebar_table = self.setup_page(soup)

            cur_page: Page = pages[page]
            
            for idx in range(len(cur_page.page_line_nos)):
                # new table row for each line
                line_str = '<pre>' + cur_page.page_line_nos[idx] + '</pre>'
                code_str = '<pre>' + cur_page.page_code_lines[idx] + '</pre>'

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
                highlight_div.append(BeautifulSoup(code_str, 'html.parser'))

                # Generating the code td
                code_table_data = soup.new_tag('td')
                code_table_data['class'] = ['code']
                code_table_data.append(highlight_div)

                table_row = soup.new_tag('tr')
                table_row.append(line_table_data)
                table_row.append(code_table_data)
                highlight_table.append(table_row)

            # End of for
            # generating table for sidebar
            self.get_pages_sidebar(cur_page.page_sidebar_line_nos, cur_page.page_sidebar_code_lines, sidebar_table, soup)
    
    def get_pages_sidebar(self, sidebar_line_nos: list, sidebar_code_lines: list, side_table, soup: BeautifulSoup):
        # side_table = self.generate_sidebar_table(soup)
        for i in range(len(sidebar_line_nos)):
            line_str = '<pre>' + str(sidebar_line_nos[i]) + '</pre>'
            code_str = '<pre>' + sidebar_code_lines[i] + '</pre>'
                
            # Generating the table row
            line_no_div = soup.new_tag('div')
            line_no_div['class'] = ['linenodiv']
            line_no_div.append(BeautifulSoup(line_str, 'html.parser'))

            line_table_data = soup.new_tag('td')
            line_table_data['class'] = ['sidelinenos']
            line_table_data.append(line_no_div)


            highlight_div = soup.new_tag('div')
            highlight_div['class'] = ['sidecode']
            highlight_div.append(BeautifulSoup(code_str, 'html.parser'))

            code_table_data = soup.new_tag('td')
            code_table_data['class'] = ['code']
            code_table_data.append(highlight_div)

            table_row = soup.new_tag('tr')
            table_row.append(line_table_data)
            table_row.append(code_table_data)

            side_table.append(table_row)
        return side_table

    def get_auxiliary_pages(self, soup: BeautifulSoup):
        self.get_augmenting_pages(self.auxiliary_partition_dict, soup)

    def get_augmenting_pages(self, augment_page_dict: dict, soup: BeautifulSoup):
        # Generate auxiliary pages using info from the existing pages.
        aux_page_count = 1
        aux_pages = {}
        # For each auxiliary partition, Check if the line is in the base page
        for aux_line in augment_page_dict:
            if aux_line not in self.line_page_dict:
                # Do something here
                pass

        # Get aux parition by page
        page_aux_dict = defaultdict(list)
        for aux_line in augment_page_dict:
            aux_part = AuxPartition(augment_page_dict[aux_line], aux_line, self.line_page_dict[aux_line])
            page_aux_dict[self.line_page_dict[aux_line]].append(aux_part)

        # Go page by page, and generate aux pages
        for page in self.pages:
            # New table for each page
            if page not in page_aux_dict:
                # Leave the page empty
                # highlight_table = self.generate_highlight_table(soup)
                continue
            else:
                # Generate the aux page
                aux_parts = page_aux_dict[page]
                cur_base_page = self.pages[page]
                cur_aux_page = Page(str(page) + '-a')
                # Nothing in the sidebar
                cur_aux_page.page_lnos = [i for i in range(cur_base_page.page_length)]
                cur_aux_page.page_line_nos = [' ' for i in range(cur_base_page.page_length)]
                cur_aux_page.page_code_lines = [' ' for i in range(cur_base_page.page_length)]
                cur_aux_page.page_sidebar_line_nos = [' ' for i in range(cur_base_page.page_length)]
                cur_aux_page.page_sidebar_code_lines = [' ' for i in range(cur_base_page.page_length)]
                aux_page_lnos = [i for i in range(cur_base_page.page_length)]
                used_lines = set()
                # print(page)
                # print(aux_page_lnos)
                # For each partition - add to page if possible
                selected_lines_set = {}
                for aPart in aux_parts:
                    idx = self.code_page_line_dict[aPart.line]
                    # idx = cur_base_page.page_lnos.index(aPart.line)
                    selected_lnos = aux_page_lnos[idx: (idx + aPart.partition.length)]
                    # print('select: ', selected_lnos)
                    # If the lengths match, and there aren't any conflicts then directly add
                    if len(selected_lnos) == aPart.partition.length:
                        selected_set = set(selected_lnos)
                        if used_lines.isdisjoint(selected_set):
                            selected_lines_set[idx] = aPart
                            used_lines = used_lines.union(selected_lnos)
                        else:
                            # Try moving it slightly up and check if it is possible to fit
                            # min_line_no = min(used_lines.intersection(selected_set))
                            # print(min_line_no)
                            # print(selected_lnos)
                            pass
                    else:
                        selected_lnos = aux_page_lnos[-aPart.partition.length:]
                        idx = aux_page_lnos.index(selected_lnos[0])
                        if used_lines.isdisjoint(set(selected_lnos)):
                            selected_lines_set[idx] = aPart
                            used_lines = used_lines.union(selected_lnos)
                
                for idx in selected_lines_set:
                    aPart = selected_lines_set[idx]
                    cur_aux_page.page_line_nos[idx:(idx + aPart.partition.length)] = [str(l) for l in aPart.partition.line_nos]
                    cur_aux_page.page_code_lines[idx:(idx + aPart.partition.length)] = aPart.partition.format_code_lines
                
                # print(used_lines)
                # print(cur_aux_page.page_line_nos)
                # print(cur_aux_page.page_code_lines)
                # print('------------------------------------------------')
                aux_pages[aux_page_count] = cur_aux_page
                aux_page_count += 1

        for page in aux_pages:
            self.all_pages.append(aux_pages[page])
        self.add_pages_html(soup, aux_pages)
    
    def get_diff_auxiliary_pages(self, soup: BeautifulSoup):
        self.get_diff_chunks()

        self.get_augmenting_pages(self.diff_auxiliary_partition_dict, soup)
        # End of function

    def get_diff_chunks(self):
        if not self.DiffInAuxiliary:
            return
        
        base_all_lines = UtilMethods.text_from_file(self.code_file.file_path).splitlines()
        base_preformatted_lines = self.code_file.preformated_all_lines
        base_line_wrap_length = self.code_file.line_wrap_length
        cmp_all_lines = UtilMethods.text_from_file(self.DiffFilePath).splitlines()
        cmp_preformatted_lines = UtilMethods.get_preformated_innerhtml('\n'.join(cmp_all_lines), self.code_file.language)
        cmp_line_wrap_length = self.code_file.wrap_lines_process(cmp_all_lines, self.code_file.MAX_LINE_LENGTH)
        lno1 = 0
        lno2 = 0
        file_diff = difflib.ndiff(base_all_lines, cmp_all_lines)
        base_chunk = []
        base_align = None
        cmp_chunk = []
        cmp_align = None

        for line in file_diff:
            code = line[:2]

            # Updating line numbers
            lno1 += 1 if (code == '  ' or code == '- ') else 0
            lno2 += 1 if (code == '  ' or code == '+ ') else 0

            # Add the change chunk
            if code == '  ':
                if base_chunk:
                    base_line_nos = base_chunk
                    base_source_code_lines = list(map(lambda x: base_all_lines[x-1], base_line_nos))
                    base_format_code_lines = list(map(lambda x: self.get_diff_rem_line(base_preformatted_lines[x-1]), base_line_nos))
                    base_part_length = sum([base_line_wrap_length[l] for l in base_line_nos])
                    base_code_part = CodePartition(base_line_nos, base_source_code_lines, base_format_code_lines, base_part_length, Node)
                    self.diff_auxiliary_partition_dict[self.get_nearest_base_line(base_align)] = base_code_part
                    base_chunk = []
                    base_align = None
                if cmp_chunk:
                    cmp_line_nos = cmp_chunk
                    cmp_source_code_lines = list(map(lambda x: cmp_all_lines[x-1], cmp_line_nos))
                    cmp_format_code_lines = list(map(lambda x: self.get_diff_add_line(cmp_preformatted_lines[x-1]), cmp_line_nos))
                    cmp_part_length = sum([cmp_line_wrap_length[l] for l in cmp_line_nos])
                    cmp_code_part = CodePartition(cmp_line_nos, cmp_source_code_lines, cmp_format_code_lines, cmp_part_length, Node)
                    self.diff_auxiliary_partition_dict[self.get_nearest_base_line(cmp_align)] = cmp_code_part
                    cmp_chunk = []
                    cmp_align = None

            if code == '+ ':
                cmp_chunk.append(lno2)
                if not cmp_align:
                    cmp_align = lno1
            elif code == '- ':
                base_chunk.append(lno1)
                if not base_align:
                    base_align = lno1
        # End of function
    
    def get_diff_rem_line(self, line: str):
        return '<span class="diffrem"> -  ' + line + '</span>'
    
    def get_diff_add_line(self, line: str):
        return '<span class="diffadd"> +  ' + line + '</span>'

    def get_nearest_base_line(self, line: int):
        tline = line
        while tline not in self.line_page_dict and tline - line < 10:
            tline += 1
        if tline in self.line_page_dict:
            return tline
        
        return line

    def pre_calculcate_pages(self, partitions: list, paper: Paper):
        # Create partition node dict
        page_count = 1
        line_count = 0
        max_lines = paper.max_lines

        for p in partitions:
            # base, side bar : create tables seperately for both
            part_length = p.base.length

            # If the new partition exceeds the page limit and the page gap is not more than half the page
            if (line_count + part_length) > max_lines and (max_lines - line_count) < max_lines/2:
                page_count += 1
                line_count = 0

            if p.node not in self.node_page_dict:
                self.node_page_dict[p.node] = page_count

            line_count += part_length
            if line_count > max_lines:
                page_count += int(line_count/max_lines)
            line_count = line_count % (max_lines)
    
    def table_of_contents(self, partitions: list):
        # iterate over function nodes and append to sidebar
        for func in self.function_nodes:
            func_base_part = self.node_parition_dict[func].base
            func_sidebar = self.node_parition_dict[func].sidebar
            call_locs = {}
            #  Get all function calls from this function and get its location
            for call in func.function_calls:
                call_line = call.start_pos.line
                cfunc = call.function_node
                if call.function_node is None:
                    continue
                cfunc_line = cfunc.start_pos.line
                cfunc_page = self.node_page_dict[cfunc]
                call_locs[call_line] = '{0} : page {1}, line {2}'.format(cfunc.name, cfunc_page, cfunc_line)
                # print(call_locs[call_line])
            # go through the partition and check if the call line already has any stuff in it
            for i in range(len(func_base_part.line_nos)):
                lno = func_base_part.line_nos[i]
                sidebar_scl = func_sidebar.source_code_lines[i]
                if lno in call_locs and sidebar_scl.strip() == '':
                    func_sidebar.source_code_lines[i] = call_locs[lno]
                    func_sidebar.format_code_lines[i] = call_locs[lno]
        return partitions

    def setup_page(self, soup: BeautifulSoup):
        html_body = soup.find('body')

        container_div = soup.new_tag('div')
        container_div['class'] = ['container']
        html_body.append(container_div)

        left_div = soup.new_tag('div')
        left_div['class'] = ['leftdiv']
        container_div.append(left_div)

        base_table = soup.new_tag('table')
        base_table['class'] = ['highlighttable']
        base_table['cellspacing'] = "0"
        left_div.append(base_table)

        right_div = soup.new_tag('div')
        right_div['class'] = ['rightdiv']
        container_div.append(right_div)

        side_table = soup.new_tag('table')
        side_table['class'] = ['highlighttable']
        side_table['cellspacing'] = "0"
        right_div.append(side_table)

        return base_table, side_table


    def generate_highlight_table(self, soup: BeautifulSoup):
        # html_body = soup.find('body')
        right_div = soup.find('div', {'class': 'leftdiv'})
        table = soup.new_tag('table')
        table['class'] = ['highlighttable']
        table['cellspacing'] = "0"
        right_div.append(table)
        return table
    
    def generate_sidebar_table(self, soup: BeautifulSoup):
        right_div = soup.find('div', {'class': 'rightdiv'})
        table = soup.new_tag('table')
        table['class'] = ['highlighttable']
        table['cellspacing'] = "0"
        right_div.append(table)
        return table
    
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
                    part = self.code_file.get_partition(current_line + 1, child.start_pos.line - 1, Node)
                    partitions.append(PagePartition(part, node))
                
                # Add the children partition
                partitions.extend(self.getPartitions(child))
                current_line = child.end_pos.line
            if current_line < end_line:
                part = self.code_file.get_partition(current_line + 1 , end_line, Node)
                partitions.append(PagePartition(part, node))
                current_line = end_line
        elif type(node) == ClassNode:
            # Print everything except the children
            current_line = node.start_pos.line - 1
            end_line = min(node.end_pos.line, len(self.code_file.all_lines))
            children = node.children
            for child in children:
                # Adding intermediate lines
                if current_line < child.start_pos.line - 1:
                    # Add a new partition
                    part = self.code_file.get_partition(current_line + 1, child.start_pos.line - 1, ClassNode)
                    partitions.append(PagePartition(part, node))
                
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
                part = self.code_file.get_partition(current_line + 1 , end_line, ClassNode)
                partitions.append(PagePartition(part, node))
                current_line = end_line
            
        elif type(node) == InterfaceNode:
            part = self.code_file.get_partition(node.start_pos.line, node.end_pos.line, InterfaceNode)
            partitions.append(PagePartition(part, node))
        elif type(node) == FunctionNode:
            if self.PushCommentsInFunction:
                function_partition = self.getFunctionPartition(node)
            else:
                part = self.code_file.get_partition(node.start_pos.line, node.end_pos.line, FunctionNode)
                function_partition = PagePartition(part, node)
            partitions.append(function_partition)
            self.node_parition_dict[node] = function_partition
            self.function_nodes.append(node)
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
                line_nos.extend(part.line_nos)
                source_code_lines.extend(part.source_code_lines)
            
            # Add the comment partition
            commentPart = self.getCommentPartition(child)
            if not(commentPart.base is None):  # Comment should be included in the base
                line_nos.extend(commentPart.base.line_nos)
                source_code_lines.extend(commentPart.base.source_code_lines)
            else:   # Comment should be a sidebar
                remaining_lines = len(line_nos) - len(sidebar_line_nos)
                if remaining_lines > 0:
                    sidebar_line_nos.extend([' ' for i in range(remaining_lines)])
                    sidebar_code.extend([' ' for i in range(remaining_lines)])
                # adding to sidebar
                sidebar_line_nos.extend(commentPart.sidebar.line_nos)
                sidebar_code.extend(commentPart.sidebar.source_code_lines)

            current_line = child.end_pos.line
        if current_line < end_line:
            # print('partition (', current_line + 1, ',', end_line, ')')
            part = self.code_file.get_partition(current_line + 1 , end_line, type(node))
            line_nos.extend(part.line_nos)
            source_code_lines.extend(part.source_code_lines)
            current_line = end_line
        
        
        base_length = sum([self.code_file.line_wrap_length[l] for l in line_nos])

        # Matching sidebar to the function length
        remaining_lines = base_length - len(sidebar_line_nos)
        if remaining_lines > 0:
            sidebar_line_nos.extend([' ' for i in range(remaining_lines)])
            sidebar_code.extend([' ' for i in range(remaining_lines)])
        
        sidebar_length = len(sidebar_line_nos)

        sidebar_part = CodePartition(
            sidebar_line_nos, 
            sidebar_code, 
            UtilMethods.get_preformated_innerhtml('\n'.join(sidebar_code), self.code_file.language),
            sidebar_length, 
            CommentNode
        )

        base_part = CodePartition(
            line_nos, 
            source_code_lines, 
            UtilMethods.get_preformated_innerhtml('\n'.join(source_code_lines), self.code_file.language),
            max(base_length, sidebar_length), 
            FunctionNode
        )

        return PagePartition(base_part, node, sidebar_part)

    def getCommentPartition(self, node: CommentNode):
        if self.hideBigComments and node.size > self.BigCommentLimit:
            part = self.code_file.get_hidden_comment_node(node.start_pos.line, node.end_pos.line, ' // ** LARGE COMMENT HIDDEN **', CommentNode)
            # Auxiliary page info
            next_line = node.end_pos.line + 1
            self.auxiliary_partition_dict[next_line] = self.code_file.get_partition(node.start_pos.line, node.end_pos.line, CommentNode)
            return PagePartition(part, node)
        elif self.pushSmallComments and node.size <= self.smallCommentLimit:
            part = self.code_file.get_partition(node.start_pos.line, node.end_pos.line, CommentNode)
            return PagePartition(node=node, sidebar=part)
        else:
            part = self.code_file.get_partition(node.start_pos.line, node.end_pos.line, CommentNode)
            return PagePartition(part, node)

    def remove_empty_partitions(self, partitions: list):
        res_partition = []
        for part in partitions:
            if part.base is None:
                res_partition.append(part)
                continue
            if not (part.sidebar is None):
                res_partition.append(part)
                continue
            base_part = part.base
            if base_part.length == 1 and base_part.source_code_lines[0].strip() == '':
                continue
            res_partition.append(part)

        return res_partition

    def squash_partitions(self, partitions: list):
        res_partition = []
        cur_sidebar = None
        for part in partitions:
            if not(part.base is None):
                if not(cur_sidebar is None):
                    if cur_sidebar.sidebar.length == 1 and part.base.length == 1 and part.base.source_code_lines[0].strip() == '':
                        part.base = cur_sidebar.sidebar
                        part.node = cur_sidebar.node
                        cur_sidebar = None
                    elif cur_sidebar.sidebar.length > part.base.length or not(part.sidebar is None):
                        # Todo: Can do better - if there is side bar, but we have initial space
                        res_partition.append(PagePartition(cur_sidebar.sidebar, cur_sidebar.node))
                        cur_sidebar = None
                    else:
                        part.sidebar = cur_sidebar.sidebar
                        cur_sidebar = None
                res_partition.append(part)
            elif not(part.sidebar is None):
                if not(cur_sidebar is None):
                    res_partition.append(PagePartition(cur_sidebar.sidebar, cur_sidebar.node))
                    cur_sidebar = None
                cur_sidebar = part
        
        if (cur_sidebar):
            res_partition.append(PagePartition(cur_sidebar.sidebar, cur_sidebar.node))
        return res_partition
    
    def get_table_for_sidebar(self, soup, partitions):
        side_table = soup.new_tag('table')
        side_table['class'] = ['sidebartable']
        side_table['cellspacing'] = "0"
        for p in partitions:
            _, pcode = UtilMethods.get_pre_formated_text(p, self.code_file.language)
            line_str = '<pre>' + '\n'.join(str(lno) for lno in p.line_nos) + '</pre>'
            
            # Generating the table row
            line_no_div = soup.new_tag('div')
            line_no_div['class'] = ['linenodiv']
            line_no_div.append(BeautifulSoup(line_str, 'html.parser'))

            line_table_data = soup.new_tag('td')
            line_table_data['class'] = ['sidelinenos']
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
