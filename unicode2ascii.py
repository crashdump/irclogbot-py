#!/usr/bin/python
# -*- coding: utf-8 -*-

# This source code is distributed under GNU GPL v2 license
# written by Victor Stinner <victor.stinner AT haypocalc.com>
#                            http://www.haypocalc.com/
# creatied: 2006-08-14 -- last change: 2007-08-17

# Convert any unicode string to ASCII string:
#  - Remove diacriticals
#  - Replace special letter with similar ASCII character (similar glyph)
#
# Support greek, cyrillic, some latin letters and some signs.

from unicodedata import normalize

UNICODE_TO_ASCII = {
    # Latin letters
    u"Æ": u"AE",   # U+00C6 (latin capital ligature ae)
    u"Ø": u"O",    # U+00D8 (latin capital letter o with stroke)
    u"ß": u"ss",   # U+00DF (latin small letter sharp s)
    u"æ": u"ae",   # U+00E6 (latin small ligature ae)
    u"ø": u"o",    # U+00F8 (latin small letter o with stroke)
    u"ł": u"l",    # U+0142 (latin small letter l with stroke)
    u"Œ": u"OE",   # U+0152 (latin capital ligature oe)
    u"œ": u"oe",   # U+0153 (latin small ligature oe)

    # Various signs
    u"¡": u"!",    # U+00A1 (inverted exclamation mark)
    u"©": u"(c)",  # U+00A9 (copyright sign)
    u"«": u'"',    # U+00AB (left-pointing double angle quotation mark)
    u"®": u"(r)",  # U+00AE (registred sign)
    u"²": u"2",    # U+00B2 (superscript two)
    u"»": u'"',    # U+00BB (right-pointing double angle quotation mark)
    u"⁄": u"/",    # U+2044 (fraction slash)

    # Greek
    u"Α": u"A",    # U+0391 (capital alpha)
    u"Β": u"B",    # U+0392 (capital beta)
    u"Ε": u"E",    # U+0395 (capital epsilon)
    u"Ζ": u"Z",    # U+0396 (capital zeta)
    u"Η": u"H",    # U+0397 (capital eta)
    u"Θ": u"O",    # U+0398 (captial theta)
    u"Ι": u"I",    # U+0399 (capital iota)
    u"Κ": u"K",    # U+039A (capital kappa)
    u"Μ": u"M",    # U+039C (capital mu)
    u"Ν": u"N",    # U+039D (capital nu)
    u"Ο": u"O",    # U+039F (capital omicron)
    u"Ρ": u"P",    # U+03A1 (capital rho)
    u"Τ": u"T",    # U+03A4 (capital tau)
    u"Υ": u"Y",    # U+03A5 (capital upsilon)
    u"Χ": u"X",    # U+03A7 (capital chi)
    u"α": u"a",    # U+03B1 (small alpha)
    u"β": u"b",    # U+03B2 (small beta)
    u"γ": u"y",    # U+03B2 (small gamma)
    u"ε": u"e",    # U+03B5 (small espilon)
    u"η": u"n",    # U+03B7 (small eta)
    u"ο": u"o",    # U+03BF (small omicron)
    u"ρ": u"p",    # U+03C1 (small rho)
    u"υ": u"v",    # U+03C1 (small upsilon)

    # Cyrillic
    u"І": u"I",    # U+0406 (capital byelorussian-ukrainian i)
    u"Ј": u"J",    # U+0408 (capital je)
    u"В": u"B",    # U+0412 (capital ve)
    u"Е": u"E",    # U+0415 (capital ie)
    u"И": u"N",    # U+0418 (capital i)
    u"З": u"3",    # U+0417 (capital ze)
    u"К": u"K",    # U+041A (capital ka)
    u"М": u"M",    # U+041C (capital em)
    u"Н": u"H",    # U+041D (capital en)
    u"О": u"O",    # U+041E (capital o)
    u"Р": u"P",    # U+0420 (capital er)
    u"С": u"C",    # U+0421 (capital es)
    u"Т": u"T",    # U+0422 (capital te)
    u"У": u"Y",    # U+0423 (capital u)
    u"Х": u"X",    # U+0425 (capital ha)
    u"Я": u"R",    # U+042F (capital ya)
    u"а": u"a",    # U+0430 (small a)
    u"в": u"b",    # U+0432 (small ve)
    u"е": u"e",    # U+0435 (small ie)
    u"з": u"3",    # U+0437 (small ze)
    u"к": u"k",    # U+043A (small ka)
    u"м": u"m",    # U+043C (small em)
    u"н": u"h",    # U+043D (small en)
    u"о": u"o",    # U+043E (small o)
    u"р": u"p",    # U+0440 (small er)
    u"с": u"c",    # U+0441 (small es)
    u"т": u"T",    # U+0442 (small te)
    u"у": u"y",    # U+0443 (small u)
    u"х": u"x",    # U+0445 (small ha)
    u"я": u"R",    # U+044F (small ya)
    u"і": u"i",    # U+0456 (small byelorussian-ukrainian i)
    u"ј": u"j",    # U+0458 (small je)
}

def unicode2ascii(text, replace=None):
    """
    Convert an unicode string (type 'unicode') to ascii string (type 'str').
    Try to keep same visual result.

    You can specify an ASCII character to replace non-ASCII character
    in 'replace' argument (eg. replace='?').

    >>> unicode2ascii(unicode("¡ Hé hø « español » ! Pythøn", "UTF-8"))
    '! He ho " espanol " ! Python'
    >>> unicode2ascii(unicode("L'œuf de læticia", "UTF-8"))
    "L'oeuf de laeticia"
    >>> unicode2ascii(unicode("ῙΈΌΑΒΓΔΕΖΗΘΙΚΛΝΜΞΟΥάήαγδεζημ", "UTF-8"), u'?')
    'IEOAB??EZHOIK?NM?OYanay?e?n?'
    >>> unicode2ascii(unicode("ЀЁЄЅІЇЈЌЍАВЕЗИКМНОРСТУХавезмнопрстухѐёіїјк", "UTF-8"), u'?')
    'EE??IIJKN?BE3NKMHOPCTYXabe3mho?pcTyxeeiijk'
    """
    assert isinstance(text, unicode)
    if replace:
        if isinstance(replace, str):
            replace = unicode(replace, "latin-1")
        if not isinstance(replace, unicode) \
        or len(replace) != 1 \
        or not (32 <= ord(replace) <= 127):
            print ValueError("invalid replace character (%r): need one ascii printable character" % replace)

    ascii = []
    for char in text:
        # Remove diacriticals
        char = normalize("NFKD", char)[0]

        # Known values
        if char in UNICODE_TO_ASCII:
            ascii.append(UNICODE_TO_ASCII[char])
            continue

        if ord(char) <= 127:
            # Add valid ASCII
            ascii.append(char)
        elif replace:
            # non-ASCII character
            ascii.append(replace)
        # else: ignore it

    text = ''.join(ascii)
    return text.encode("ascii", "strict")

if __name__ == "__main__":
    from doctest import testmod
    from sys import exit
    failure, total = testmod()
    if failure:
        print "%s failure on %s tests" % (failure, total)
        exit(1)
    else:
        print "All tests are OK (count=%s)" % total

