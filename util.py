import nltk
from nltk.stem import WordNetLemmatizer


ns_prefix = '{http://xml.house.gov/schemas/uslm/1.0}'
def prefix_tag(tag):
    return ns_prefix + tag


new_line_tags = {prefix_tag(tag)
                 for tag in ['section', 'subsection', 'paragraph', 'subparagraph', 'clause', 'subclause']}
def is_newline_tag(tag):
    return tag in new_line_tags


def is_uscode_id(elem_id):
    return elem_id.startswith('/us/usc')


def trim_id(elem_id, start, end):
    return '/'.join(elem_id.split('/')[start:end])


def format_title_id(elem_id):
    return trim_id(elem_id, 3, 4)


def format_section_id(elem_id):
    return trim_id(elem_id, 3, 5)


nltk.download('wordnet', quiet=True)
lemmatize = WordNetLemmatizer().lemmatize
def transform_word(word):
    return lemmatize(lemmatize(word.lower(), 'n'), 'v')
