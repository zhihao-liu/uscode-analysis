import nltk
from nltk.stem import WordNetLemmatizer


nltk.download('wordnet', quiet=True)
lemmatize = WordNetLemmatizer().lemmatize


def extract_title_id(section_id):
    return section_id.split('/')[0]


def transform_word(word):
    return lemmatize(lemmatize(word.lower(), 'n'), 'v')


def dict_distance(dict1, dict2):
    keys = dict1.keys() & dict1.keys()
    return sum((dict1.get(k, 0) - dict2.get(k, 0)) ** 2 for k in keys) ** 0.5
