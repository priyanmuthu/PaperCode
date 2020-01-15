import pygments
from pygments import lexers, formatters, styles

class Highlighter:
    def highlight_file(self, input_file, linenos=True, style='default'):
        """ Highlight the input file, and return HTML as a string. """
        try:
            lexer = lexers.get_lexer_for_filename(input_file)
        except pygments.util.ClassNotFound:
            # Try guessing the lexer (file type) later.
            lexer = None

        try:
            formatter = formatters.HtmlFormatter(
                linenos='table',
                style=style,
                full=True)
        except pygments.util.ClassNotFound:
            # logging.error("\nInvalid style name: {}\nExpecting one of:\n \
            #     {}".format(style, "\n    ".join(sorted(styles.STYLE_MAP))))
            # sys.exit(1)
            print("\nInvalid style name: {}\nExpecting one of:\n \
                {}".format(style, "\n    ".join(sorted(styles.STYLE_MAP))))

        try:
            with open(input_file, "r") as f:
                content = f.read()
                try:
                    lexer = lexer or lexers.guess_lexer(content)
                except pygments.util.ClassNotFound:
                    # No lexer could be guessed.
                    lexer = lexers.get_lexer_by_name("text")
        except EnvironmentError as exread:
            fmt = "\nUnable to read file: {}\n{}"
            print(fmt.format(input_file, exread))
            # logging.error(fmt.format(input_file, exread))
            # sys.exit(2)

        return pygments.highlight(content, lexer, formatter)
