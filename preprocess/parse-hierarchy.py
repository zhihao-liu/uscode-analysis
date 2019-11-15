import argparse
import os
from collections import Counter
import json
from xml.etree import ElementTree as ET
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from uscode import util


nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

stop_words = set(stopwords.words('english'))
xml_prefix = '{http://xml.house.gov/schemas/uslm/1.0}'


def extract_section_text(elem):
    return ''.join(elem.itertext())


def prefix_tag(tag):
    return xml_prefix + tag


def extract_tag(tag):
    return tag[len(xml_prefix):]


def get_uscode_id(elem, key='identifier', s=slice(3, None)):
    elem_id = elem.attrib.get(key)
    return trim_id(elem_id, s) if is_uscode_id(elem_id) else None


def is_uscode_id(elem_id):
    return elem_id is not None and elem_id.startswith('/us/usc')


def trim_id(elem_id, s):
    return '/'.join(elem_id.split('/')[s])


def preprocess_xml(dir_path):
    titles = {}
    usc = {'titles': titles}

    for filename in os.listdir(dir_path):
        if (os.path.splitext(filename)[1] != '.xml'): continue

        print("Processing {}...".format(filename))
        root = ET.parse(os.path.join(dir_path, filename)).getroot()

        title_elem = next(root.iter(prefix_tag('title')), None)
        if title_elem is None: continue
        title_id = get_uscode_id(title_elem)
        if not title_id: continue

        chapters = {}
        titles[title_id] = {'id': title_id, 'chapters': chapters}

        for chap_elem in root.iter(prefix_tag('chapter')):
            chap_id = get_uscode_id(chap_elem)
            if not chap_id: continue

            sections = {}
            chapters[chap_id] = {'id': chap_id, 'sections': sections}

            for sec_elem in chap_elem.iter(prefix_tag('section')):
                sec_id = get_uscode_id(sec_elem)
                if not sec_id: continue

                sec_text = extract_section_text(sec_elem)

                terms = (util.transform_word(w) for w in word_tokenize(sec_text) if w not in stop_words)
                term_counter = Counter(terms)

                ref_counter = Counter()
                for ref_elem in sec_elem.iter(prefix_tag('ref')):
                    ref_id = get_uscode_id(ref_elem, 'href', slice(3, 5))
                    if not ref_id: continue
                    ref_counter[ref_id] += 1

                sections[sec_id] = {'id': sec_id,
                                    'text': sec_text,
                                    'terms': term_counter,
                                    'refs': ref_counter}

    return usc


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('input_dir')
    arg_parser.add_argument('-o', '--output_file', required=True)

    args = arg_parser.parse_args()

    usc_dict = preprocess_xml(args.input_dir)
    with open(args.output_file, 'x') as f:
        json.dump(usc_dict, f)
