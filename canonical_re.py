import re
import argparse
from re import escape
from typing import Match
from binascii import hexlify
from string import ascii_letters, digits

"""
Build Regular Expressions that search for canonical variations of characters within the given strings
Using case-insensitivity will provide a 3tuple (?:z|%7[aA]|%5[aA])
Case-sensitivity provides a 2tuple (?:z|%7[aA])
"""
def to_hex(value) -> str: return hexlify(value.encode()).decode()

def craft_char_class(m:Match) -> str:
    return f"{m.group(1)}[{m.group(2).lower()}{m.group(2).upper()}]"if m.group(2) else f"{m.group(1)}"

def sub_char_class(hex_value) -> str: return re.sub(r'([0-9]*)([a-zA-Z]*)',craft_char_class,hex_value)

def get_split_case(c:str) -> str:
    if c.isalpha():
        return f"(?:{c}|%{sub_char_class(to_hex(c.lower()))}|%{sub_char_class(to_hex(c.upper()))})"
    return f"(?:{c}|%{sub_char_class(to_hex(c.lower()))})"

def get_single_case(c:str) -> str: return f"(?:{c}|%{to_hex(c) if c.isdigit() else sub_char_class(to_hex(c))})"

def canonicalize(text, full_ascii=False, case_insensitive=False) -> str:
    exclude = [] if full_ascii else ascii_letters + digits
    ret = []
    if case_insensitive:
        [ret.append(get_split_case(escape(i)) if i not in exclude else i) for i in text]
        return "(?i)" + ''.join(ret)
    else:
        [ret.append(get_single_case(escape(i)) if i not in exclude else i) for i in text]
        return ''.join(ret)

def find_all(*args): return '(?:'+'|'.join([exp for exp in args]) + ')'

def scan_inline(*args,join='.+'): return join.join([exp for exp in args])

def get_params() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Give me some canonical variations for my string')
    parser.add_argument("strings",
                        nargs='+',
                        help="strings to convert")
    parser.add_argument("-i","--case-insensitive",
                        action='store_true',
                        help="give a case insensitive 3-tuple")
    parser.add_argument("-a", "--full-ascii",
                        action='store_true',
                        help="Convert all ascii characters.")
    builder = parser.add_mutually_exclusive_group()
    builder.add_argument("--inline",
                        const='.*',
                        nargs='?',
                        help="Craft an [expression] joined expression for your strings. "
                             "'.+' is used if no value is passed in")
    builder.add_argument("--findall",
                        action='store_true',
                        help="Craft an alternate capture group of your separate strings")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_params()
    expressions = []
    [expressions.append(canonicalize(i,full_ascii=args.full_ascii,case_insensitive=args.case_insensitive))
     for i in args.strings]

    if args.findall:
        print(find_all(*expressions))
    elif args.inline:
        print(scan_inline(*expressions,join=args.inline))
    else:
        [print(e) for e in expressions]





