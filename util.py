from boolean import BooleanAlgebra


ns_prefix = '{http://xml.house.gov/schemas/uslm/1.0}'
new_line_tags = {'section', 'subsection', 'paragraph', 'subparagraph', 'clause', 'subclause'}
boolean = BooleanAlgebra()


def prefix_tag(tag):
    return ns_prefix + tag


def is_newline_tag(tag):
    return deprefix_tag(tag) in new_line_tags


def contains_text(elem, text):
    text = text.lower()
    return any(child.text and text in child.text.lower() for child in elem.iter(prefix_tag('content')))


def booleanify(val):
    return boolean.TRUE if val else boolean.FALSE


def is_uscode_id(elem_id):
    return elem_id.startswith('/us/usc')


def id_level(elem_id, level):
    return '/'.join(elem_id.split('/')[:level])
