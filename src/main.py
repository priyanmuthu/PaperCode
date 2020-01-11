from language import parser

def main():
    p = parser.Parser()
    print(p.parse_expression("1+2"))


if __name__ == "__main__":
    main()