import libcst

class Parser:
    def __init__(self):
        pass
    def parse_expression(self, exp_str):
        return libcst.parse_expression(exp_str)
    def parse_statement(self, stat_str):
        return libcst.parse_statement(stat_str)
    def parse_module(self, module_str):
        return libcst.parse_module(module_str)
    def parse_module_with_metadata(self, module_str):
        return libcst.metadata.MetadataWrapper(libcst.parse_module(module_str))