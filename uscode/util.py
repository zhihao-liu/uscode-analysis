import nltk
from nltk.stem import WordNetLemmatizer


xml_prefix = '{http://xml.house.gov/schemas/uslm/1.0}'
nltk.download('wordnet', quiet=True)
lemmatize = WordNetLemmatizer().lemmatize


def prefix_tag(tag):
    return xml_prefix + tag


def extract_tag(tag):
    return tag[len(xml_prefix):]


def is_newline_tag(tag):
    return extract_tag(tag) in new_line_tags


def is_uscode_id(elem_id):
    return elem_id.startswith('/us/usc')


def trim_id(elem_id, start, end):
    return '/'.join(elem_id.split('/')[start:end])


def format_title_id(elem_id):
    return trim_id(elem_id, 3, 4)


def format_section_id(elem_id):
    return trim_id(elem_id, 3, 5)


def extract_title_id(section_id):
    return section_id.split('/')[0]


def stringify_section(elem):
    return ''.join(elem.itertext())


def transform_word(word):
    return lemmatize(lemmatize(word.lower(), 'n'), 'v')


def dict_distance(dict1, dict2):
    keys = dict1.keys() & dict1.keys()
    return sum((dict1.get(k, 0) - dict2.get(k, 0)) ** 2 for k in keys) ** 0.5


def group_by_label(items, labels):
    groups = {}
    for item, label in zip(items, labels):
        groups.setdefault(label, []).append(item)
    return groups
