import argparse
import os
from collections import Counter
import json
from xml.etree import ElementTree as ET
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from lib import util


nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))


def preprocess_xml(dir_path):
    titles = {}
    usc = {'titles': titles}

    for filename in os.listdir(dir_path):
        print("Processing {}...".format(filename))

        root = ET.parse(os.path.join(dir_path, filename)).getroot()

        xml_main = root.find(util.prefix_tag('main'))
        if not xml_main:
            continue

        title_elem = xml_main.find(util.prefix_tag('title'))
        if not title_elem:
            continue

        title_id = title_elem.attrib.get('identifier')
        if not title_id or not util.is_uscode_id(title_id):
            continue
        title_id = util.format_title_id(title_id)

        sections = {}
        titles[title_id] = {'id': title_id, 'sections': sections}

        for sec_elem in root.iter(util.prefix_tag('section')):
            sec_id = sec_elem.attrib.get('identifier')
            if not sec_id or not util.is_uscode_id(sec_id):
                continue
            sec_id = util.format_section_id(sec_id)

            sec_text = util.stringify_section(sec_elem)

            terms = (util.transform_word(w)
                     for w in word_tokenize(sec_text) if w not in stop_words)
            term_counter = Counter(terms)

            ref_counter = Counter()
            for ref_elem in sec_elem.iter(util.prefix_tag('ref')):
                ref_id = ref_elem.attrib.get('href')
                if not ref_id or not util.is_uscode_id(ref_id):
                    continue
                ref_id = util.format_section_id(ref_id)

                ref_counter[ref_id] += 1

            sections[sec_id] = {'id': sec_id,
                                'text': sec_text,
                                'terms': term_counter,
                                'refs': ref_counter}

    return usc


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', '--input-dir', dest='input_dir_path', required=True)
    arg_parser.add_argument('-o', '--output', dest='output_path', required=True)

    args = arg_parser.parse_args()

    usc_dict = preprocess_xml(args.input_dir_path)
    with open(args.output_path, 'x') as f:
        json.dump(usc_dict, f)
