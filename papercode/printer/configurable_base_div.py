from papercode.printer.base_div import BaseDiv
from papercode.common.utils import UtilMethods, Paper
from papercode.language.node import Node, ClassNode, FunctionNode, CallNode, InterfaceNode, CommentNode
from papercode.printer.code_file import CodeFile, CodePartition
from bs4 import BeautifulSoup
from collections import defaultdict
from os.path import abspath
import difflib
import uuid

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
        self.page_no = page_no

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
            block_length = part_length
            if (line_count + block_length) > max_lines and (max_lines - line_count) < max_lines/2:
                # Start a new page
                self.pages[page_count] = current_page
                page_count += 1
                line_count = 0
                current_page = Page(str(page_count))
            lnos = p.base.line_nos
            line_nos = [str(lno) for lno in p.base.line_nos]
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

            for i in range(part_length):
                if (line_count + 1) > max_lines:
                    self.pages[page_count] = current_page
                    page_count += 1
                    line_count = 0
                    current_page = Page(str(page_count))
                
                line_count += 1
                self.line_page_dict[lnos[i]] = page_count
                current_page.page_lnos.append(lnos[i])
                current_page.page_line_nos.append(line_nos[i])
                current_page.page_code_lines.append(code_lines[i])
                if sidebar_line_nos and sidebar_code_lines and i < sidebar_length:
                    current_page.page_sidebar_line_nos.append(sidebar_line_nos[i])
                    current_page.page_sidebar_code_lines.append(sidebar_code_lines[i])
                else:
                    current_page.page_sidebar_line_nos.append(' ')
                    current_page.page_sidebar_code_lines.append(' ')

        if len(current_page.page_line_nos) > 0:
            # There are still some code left
            self.pages[page_count] = current_page
            page_count += 1
            line_count = 0
            current_page = Page(str(page_count))

        self.add_pages_html(soup, self.pages)
        
    def add_pages_html(self, soup: BeautifulSoup, pages: dict):
        # Generate a table for each page
        for page in pages:
            highlight_table = self.generate_highlight_table(soup)
            page_line_nos = pages[page].page_line_nos
            page_code_lines = pages[page].page_code_lines
            page_sidebar_line_nos = pages[page].page_sidebar_line_nos
            page_sidebar_code_lines = pages[page].page_sidebar_code_lines
            # For each line create a table row
            line_str = '<pre>' + '\n'.join(page_line_nos) + '</pre>'
            code_str = '<pre>' + '\n'.join(page_code_lines) + '</pre>'
            
            # Generate QR-Code and header/footer elements
            # qr_td_1 = soup.new_tag('td')
            # qr_td_1['style'] = "position:relative;"

            # qr_td_2 = soup.new_tag('td')
            # qr_td_2['style'] = "position:relative;"

            # qr_td_3 = soup.new_tag('td')
            # qr_td_3['style'] = "position:relative;"
            # qrcode = soup.new_tag('img')
            # qrcode['class'] = ['qrcode']
            # qrcode['src'] = "data:image/png;base64,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"
            # qr_td_3.append(qrcode)

            # qr_td_4 = soup.new_tag('td')
            # qr_td_4['style'] = "position:relative;"
            
            # qr_table_row = soup.new_tag('tr')
            # qr_table_row.append(qr_td_1)
            # qr_table_row.append(qr_td_2)
            # qr_table_row.append(qr_td_3)
            # qr_table_row.append(qr_td_4)
            # highlight_table.append(qr_table_row)

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

            # Generating the side bar table
            sidebar_table_data = soup.new_tag('td')
            sidebar_table_data['class'] = ['sidebar']
            side_table = self.get_pages_sidebar(page_sidebar_line_nos, page_sidebar_code_lines, soup)
            sidebar_table_data.append(side_table)

            table_row = soup.new_tag('tr')
            table_row.append(line_table_data)
            table_row.append(code_table_data)
            table_row.append(sidebar_table_data)
            highlight_table.append(table_row)
    
    def get_pages_sidebar(self, sidebar_line_nos: list, sidebar_code_lines: list, soup: BeautifulSoup):
        side_table = soup.new_tag('table')
        side_table['class'] = ['sidebartable']
        side_table['cellspacing'] = "0"

        line_str = '<pre>' + '\n'.join(str(lno) for lno in sidebar_line_nos) + '</pre>'
        code_str = '<pre>' + '\n'.join(sidebar_code_lines) + '</pre>'
            
        # Generating the table row
        line_no_div = soup.new_tag('div')
        line_no_div['class'] = ['linenodiv']
        line_no_div.append(BeautifulSoup(line_str, 'html.parser'))

        line_table_data = soup.new_tag('td')
        line_table_data['class'] = ['sidelinenos']
        line_table_data.append(line_no_div)


        highlight_div = soup.new_tag('div')
        highlight_div['class'] = ['highlight']
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
        # Generate auxiliary pages using info from the existing pages.
        aux_page_count = 1
        aux_pages = {}
        # For each auxiliary partition, Check if the line is in the base page
        for aux_line in self.auxiliary_partition_dict:
            if aux_line not in self.line_page_dict:
                # Do something here
                pass

        # Get aux parition by page
        page_aux_dict = defaultdict(list)
        for aux_line in self.auxiliary_partition_dict:
            print(aux_line, self.line_page_dict[aux_line])
            aux_part = AuxPartition(self.auxiliary_partition_dict[aux_line], aux_line, self.line_page_dict[aux_line])
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
                cur_aux_page.page_line_nos = [' ' for i in range(len(cur_base_page.page_lnos))]
                cur_aux_page.page_code_lines = [' ' for i in range(len(cur_base_page.page_lnos))]
                cur_aux_page.page_sidebar_line_nos = [' ' for i in range(len(cur_base_page.page_lnos))]
                cur_aux_page.page_sidebar_code_lines = [' ' for i in range(len(cur_base_page.page_lnos))]
                used_lines = set()
                print(page)
                # For each partition - add to page if possible
                for aPart in aux_parts:
                    idx = cur_base_page.page_lnos.index(aPart.line)
                    selected_lnos = cur_base_page.page_lnos[idx: (idx + aPart.partition.length)]
                    # If the lengths match, and there aren't any conflicts then directly add
                    if len(selected_lnos) == aPart.partition.length:
                        selected_set = set(selected_lnos)
                        if used_lines.isdisjoint(selected_set):
                            used_lines = used_lines.union(selected_lnos)
                            cur_aux_page.page_line_nos[idx:(idx + aPart.partition.length)] = [str(l) for l in aPart.partition.line_nos]
                            cur_aux_page.page_code_lines[idx:(idx + aPart.partition.length)] = aPart.partition.format_code_lines
                        else:
                            # Try moving it slightly up and check if it is possible to fit
                            # min_line_no = min(used_lines.intersection(selected_set))
                            # print(min_line_no)
                            # print(selected_lnos)
                            pass
                    else:
                        selected_lnos = cur_base_page.page_lnos[-aPart.partition.length:]
                        idx = cur_base_page.page_lnos.index(selected_lnos[0])
                        if used_lines.isdisjoint(set(selected_lnos)):
                            used_lines = used_lines.union(selected_lnos)
                            cur_aux_page.page_line_nos[idx:(idx + aPart.partition.length)] = [str(l) for l in aPart.partition.line_nos]
                            cur_aux_page.page_code_lines[idx:(idx + aPart.partition.length)] = aPart.partition.format_code_lines
                    print(aPart.partition.length, len(selected_lnos), selected_lnos)
                pass
                print(used_lines)
                # print(cur_aux_page.page_line_nos)
                # print(cur_aux_page.page_code_lines)
                print('------------------------------------------------')
                aux_pages[aux_page_count] = cur_aux_page
                aux_page_count += 1

        self.add_pages_html(soup, aux_pages)
    
    def get_diff_auxiliary_pages(self, soup: BeautifulSoup):
        self.get_diff_chunks()

        aux_page_count = 1
        aux_pages = {}

        # Get aux parition by page
        page_aux_dict = defaultdict(list)
        for aux_line in self.diff_auxiliary_partition_dict:
            print(aux_line, self.line_page_dict[aux_line])
            aux_part = AuxPartition(self.diff_auxiliary_partition_dict[aux_line], aux_line, self.line_page_dict[aux_line])
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
                cur_aux_page.page_line_nos = [' ' for i in range(len(cur_base_page.page_lnos))]
                cur_aux_page.page_code_lines = [' ' for i in range(len(cur_base_page.page_lnos))]
                cur_aux_page.page_sidebar_line_nos = [' ' for i in range(len(cur_base_page.page_lnos))]
                cur_aux_page.page_sidebar_code_lines = [' ' for i in range(len(cur_base_page.page_lnos))]
                used_lines = set()
                # print(page)
                # For each partition - add to page if possible
                for aPart in aux_parts:
                    idx = cur_base_page.page_lnos.index(aPart.line)
                    selected_lnos = cur_base_page.page_lnos[idx: (idx + aPart.partition.length)]
                    # If the lengths match, and there aren't any conflicts then directly add
                    if len(selected_lnos) == aPart.partition.length:
                        selected_set = set(selected_lnos)
                        if used_lines.isdisjoint(selected_set):
                            used_lines = used_lines.union(selected_lnos)
                            cur_aux_page.page_line_nos[idx:(idx + aPart.partition.length)] = [str(l) for l in aPart.partition.line_nos]
                            cur_aux_page.page_code_lines[idx:(idx + aPart.partition.length)] = aPart.partition.format_code_lines
                        else:
                            # Try moving it slightly up and check if it is possible to fit
                            # min_line_no = min(used_lines.intersection(selected_set))
                            # print(min_line_no)
                            # print(selected_lnos)
                            pass
                    else:
                        selected_lnos = cur_base_page.page_lnos[-aPart.partition.length:]
                        idx = cur_base_page.page_lnos.index(selected_lnos[0])
                        if used_lines.isdisjoint(set(selected_lnos)):
                            used_lines = used_lines.union(selected_lnos)
                            cur_aux_page.page_line_nos[idx:(idx + aPart.partition.length)] = [str(l) for l in aPart.partition.line_nos]
                            cur_aux_page.page_code_lines[idx:(idx + aPart.partition.length)] = aPart.partition.format_code_lines
                    print(aPart.partition.length, len(selected_lnos), selected_lnos)
                pass
                # print(used_lines)
                # print(cur_aux_page.page_line_nos)
                # print(cur_aux_page.page_code_lines)
                # print('------------------------------------------------')
                aux_pages[aux_page_count] = cur_aux_page
                aux_page_count += 1

        self.add_pages_html(soup, aux_pages)

        # End of function

    def get_diff_chunks(self):
        if not self.DiffInAuxiliary:
            return
        
        base_all_lines = UtilMethods.text_from_file(self.code_file.file_path).splitlines()
        base_preformatted_lines = self.code_file.preformated_all_lines
        cmp_all_lines = UtilMethods.text_from_file(self.DiffFilePath).splitlines()
        cmp_preformatted_lines = UtilMethods.get_preformated_innerhtml('\n'.join(cmp_all_lines), self.code_file.language)
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
                    base_code_part = CodePartition(base_line_nos, base_source_code_lines, base_format_code_lines, len(base_line_nos), Node)
                    self.diff_auxiliary_partition_dict[self.get_nearest_base_line(base_align)] = base_code_part
                    base_chunk = []
                    base_align = None
                if cmp_chunk:
                    cmp_line_nos = cmp_chunk
                    cmp_source_code_lines = list(map(lambda x: cmp_all_lines[x-1], cmp_line_nos))
                    cmp_format_code_lines = list(map(lambda x: self.get_diff_add_line(cmp_preformatted_lines[x-1]), cmp_line_nos))
                    cmp_code_part = CodePartition(cmp_line_nos, cmp_source_code_lines, cmp_format_code_lines, len(cmp_line_nos), Node)
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
            block_length = part_length

            # If the new partition exceeds the page limit and the page gap is not more than half the page
            if (line_count + block_length) > max_lines and (max_lines - line_count) < max_lines/2:
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
            for i in range(func_base_part.length):
                lno = func_base_part.line_nos[i]
                sidebar_scl = func_sidebar.source_code_lines[i]
                if lno in call_locs and sidebar_scl.strip() == '':
                    func_sidebar.source_code_lines[i] = call_locs[lno]
                    func_sidebar.format_code_lines[i] = call_locs[lno]
        return partitions

    def generate_highlight_table(self, soup: BeautifulSoup):
        html_body = soup.find('body')
        table = soup.new_tag('table')
        table['class'] = ['highlighttable']
        table['cellspacing'] = "0"
        html_body.append(table)
        return table


    def get_table_row_from_partition(self, soup: BeautifulSoup, part: dict):
        # Making the base
        base_part = part.base
        part_uuid = uuid.uuid4().hex
        _, code_base = UtilMethods.get_pre_formated_text(base_part, self.code_file.language)
        # code_base = code_base.splitlines()[:base_part['length']]
        # code_base = '\n'.join(code_base)
        line_str = '<pre>' + '\n'.join(str(lno) for lno in base_part.line_nos) + '</pre>'
        
        if base_part['partition_type'] == FunctionNode:
            lines = [str(lno) for lno in base_part.line_nos]
            lines[0] = '<span class="boldlinenos">' + lines[0] + '</span>'
            line_str = '<pre>' + '\n'.join(lines) + '</pre>'
        
        # Generating the line no div
        line_no_div = soup.new_tag('div')
        line_no_div['class'] = ['linenodiv']
        line_no_div.append(BeautifulSoup(line_str, 'html.parser'))
        
        # Generating the line no td
        line_table_data = soup.new_tag('td')
        if part.node not in self.elements_line_td:
            self.elements_line_td[part.node] = part_uuid + '-line'
            line_table_data['id'] = self.elements_line_td[part.node]
        line_table_data['class'] = ['linenos']
        line_table_data.append(line_no_div)

        # Generating the code highlight div
        highlight_div = soup.new_tag('div')
        highlight_div['class'] = ['highlight']
        highlight_div.append(BeautifulSoup(code_base, 'html.parser'))

        # Generating the code td
        code_table_data = soup.new_tag('td')
        if part.node not in self.elements_code_td:
            self.elements_code_td[part.node] = part_uuid + '-code'
            code_table_data['id'] = self.elements_code_td[part.node]
        code_table_data['class'] = ['code']
        code_table_data.append(highlight_div)

        # Generating the side bar table
        sidebar_table_data = soup.new_tag('td')
        if part.node not in self.elements_sidebar_td:
            self.elements_sidebar_td[part.node] = part_uuid + '-sidebar'
            sidebar_table_data['id'] = self.elements_sidebar_td[part.node]
        sidebar_table_data['class'] = ['sidebar']
        if not(part.sidebar is None) and part.sidebar.length > 0:
            side_table = self.get_table_for_sidebar(soup, [part.sidebar])
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
            if not(commentPart.base is None):
                line_nos.extend(commentPart.base.line_nos)
                source_code_lines.extend(commentPart.base.source_code_lines)
            else:
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
        
        # Matching sidebar to the function length
        remaining_lines = len(line_nos) - len(sidebar_line_nos)
        if remaining_lines > 0:
            sidebar_line_nos.extend([' ' for i in range(remaining_lines)])
            sidebar_code.extend([' ' for i in range(remaining_lines)])
        
        sidebar_part = CodePartition(
            sidebar_line_nos, 
            sidebar_code, 
            UtilMethods.get_preformated_innerhtml('\n'.join(sidebar_code), self.code_file.language),
            len(sidebar_line_nos), 
            CommentNode
        )

        base_part = CodePartition(
            line_nos, 
            source_code_lines, 
            UtilMethods.get_preformated_innerhtml('\n'.join(source_code_lines), self.code_file.language),
            max(len(line_nos), len(sidebar_line_nos)), 
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
