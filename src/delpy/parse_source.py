# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import re

from delpy.lib.pyparsing import *


# // comment
#pCommentCStyleOneline = '//' + restOfLine
pCommentCStyleOneline = Regex(r'//.*')
# { comment } -- also captures compiler directive {$WARNINGS OFF}
pCommentBraces = QuotedString('{', endQuoteChar='}', multiline=True)
# (* comment *)
# XXX BUG when greedy, thus make single line
# XXX BUG when not killing the multiline comment produces erroneous parses from
# within the comment
pCommentParens = QuotedString('(*', endQuoteChar='*)', multiline=True)

def unifyNewlines(s):
    '''Make all newlines CRLF (dos)'''
#    return re.sub('(?<!\r)\n', '\r\n', s)
    return re.sub('\r\n', '\n', s)

def transStrip(s, parser):
    return parser.setParseAction(replaceWith('')).transformString(s)

def transStripCommentsORIG(s):
    '''C style online comments have to be stripped first, but on the whole it's
    faster to do each type in turn'''
    # timing on Windows.pas after dos2unix

    # recommended : 25.45s
#    s = Suppress(pCommentCStyleOneline | pCommentBraces | pCommentParens).transformString(s)

    # rewritten : 18.96s
#    s = Suppress(pCommentBraces).transformString(s)
#    s = Suppress(pCommentParens).transformString(s)
#    s = Suppress(pCommentCStyleOneline).transformString(s)

    # oldest known optimal : 13.00s
#    s = transStrip(s, pCommentBraces)
#    s = transStrip(s, pCommentParens)
#    s = transStrip(s, pCommentCStyleOneline)

    # regex method : 0.11s
    s = re.sub('(?m)[{][^}]*[}]', '', s)
    s = re.sub('(?ms)[(][*].*?[*][)]', '', s)
    s = re.sub('[/][/].*', '', s)
    return s

def manualStripComments(s, keep_directives=False, keep_all_directives=False):
    # timing: 0.85s
    kept_directives = '(?i)^[$](?:r|l(?:ink)?)[ ].*'
    if keep_all_directives:
        kept_directives = '^[$].*'
    t = ''          # result string
    cur = 0         # cursor, position in s
    copycur = 0     # cursor indicating up to which point in s, t has been filled
    slen = len(s)   # precompute length of s
    while cur < slen:
        c = s[cur]

        # handle single quoted string, back to back strings also work:
        #  'a string with a quote''d word'
        if c == "'":                # find leading quote
            cur += 1                # move past it
            while s[cur] != "'":    # advance until end quote
                cur += 1
            cur += 1                # move past it

        # handle brace comments:
        #  { comment }
        elif c == '{':              # find opening brace
            if (keep_directives         # if we're keeping directives,
                and re.match(kept_directives, s[cur+1:cur+7])):
                cur += 1                # and move past it
            else:
                t += s[copycur:cur]     # fill t because we introduce discontinuity
                t += ' '                # don't join tokens sep. only by a comment

                while s[cur] != '}':    # find end brace
                    cur += 1
                cur += 1                # move past it

                copycur = cur           # set copy marker at the end of comment

        # handle parens comments:
        #  (* comment *)
        elif c == '(':                      # find opening paren
            cur += 1                        # advance to check for asterisk
            if s[cur] == '*':               # if found, we have the comment
                if (keep_directives         # if we're keeping directives,
                    and re.match(kept_directives, s[cur+1:cur+7])):
                    cur += 1                # and move past it
                else:
                    t += s[copycur:cur-1]       # fill t up to this point
                    t += ' '                    # don't join tokens

                    cur += 1                    # move past asterisk
                    while not (s[cur] == '*' and    # find *)
                               s[cur+1] == ')'):
                        cur += 1
                    cur += 2                    # move past *)

                    copycur = cur               # set copy marker

        # handle c comments:
        #  // comment
        elif c == '/':                      # find /
            cur += 1                        # advance to check for second /
            if s[cur] == '/':               # if found, we have the comment
                t += s[copycur:cur-1]       # fill t up to this point

                while s[cur] != '\n':       # find end of line, don't consume
                    cur += 1

                copycur = cur               # set copy marker
        else:
            cur += 1    # advance cursor

    if copycur < cur:
        t += s[copycur:]    # fill into t what is left of s uncopied
    return t

def transStripComments(s, *args, **kw):
    try:
        return manualStripComments(s, *args, **kw)
    except IndexError:  # should only be triggered by syntax error
        return s

pSpace = White(ws=' ').suppress()
pWhite = White().suppress()

pLiteral = lambda t: Suppress(t)
pIliteral = lambda t: Suppress(CaselessLiteral(t))

# ex: RegExWrapper_TLB
# pUnitName = Word(alphas, alphanums)
pUnitName = Regex('[a-zA-Z_][a-zA-Z0-9_]*') # include underscore

# ex: System.Drawing
pUnitNameNamespaced = Combine(
    pUnitName
    + ZeroOrMore('.' + pUnitName)
)

def get_pFileHeader():
    program = CaselessLiteral('program')
    library = CaselessLiteral('library')
    package = CaselessLiteral('package')
    unit = CaselessLiteral('unit')

    # ex: program Abysmal;
    pFileHeader = (
        (program
         | library
         | package
         | unit
        )
        + pSpace
        + pUnitNameNamespaced
        + pLiteral(';')
    )

    return pFileHeader

def get_pAbstractImports(keyword):
    # ex: HomeU in 'HomeU.pas'
    pUnitUse = (
        pUnitNameNamespaced
        + Optional(
            pSpace
            + pIliteral('in')
            + pSpace
            + ( QuotedString("'") | QuotedString('"') )
        )
    )

    # ex: uses Windows, Messages, SysUtils;
    pUses = (
        pIliteral(keyword)
        + pWhite
        + delimitedList(Group(pUnitUse), delim=',')
        + pIliteral(';')
    )

    return pUses

def get_pUses():
    return get_pAbstractImports('uses')

def get_pContains():
    return get_pAbstractImports('contains')

def get_pInclude():
    # ex: {$I vars.pas.inc}  # include file
    pInclude = (
         (pIliteral('{$I ') | pIliteral('{$Include '))
        + SkipTo('}')
        + pLiteral('}')
    )
    return pInclude

def get_pResource():
    def post(s,l,toks):
        # ex: {$R '..\Source\SynEditReg.dcr'}
        # ex: {$R 'UserControls\ucMenu.TucMenu.resources' 'UserControls\ucMenu.resx'}
        pFiles = (
            OneOrMore(QuotedString("'", endQuoteChar="'"))
        ) | Empty()
        st = pFiles.parseString(toks[0])
        if not st.asList():
            return toks
        return st

    # ex: {$R *.res}
    # ex: {$L file.obj}     # link object file
    # ex: {$LINK file.obj}  # link object file
    pResource = (
        (pIliteral('{$R ') | pIliteral('{$L ') | pIliteral('{$LINK '))
        + SkipTo('}')
        + pLiteral('}')
    ).setParseAction(post)

    return pResource
