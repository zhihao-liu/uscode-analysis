import argparse
import os
import re
from collections import Counter
import itertools
import json
from xml.etree import ElementTree as ET
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from uscode import util


nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))

ref_pattern = re.compile('section ([0-9]\\w*)(?: of title ([0-9]\\w*)| of this title)', re.IGNORECASE)


def preprocess_xml(dir_path):
    titles = {}
    usc = {'titles': titles}

    for filename in os.listdir(dir_path):
        if (os.path.splitext(filename)[1] != '.xml'):
            continue
        print("Processing {}...".format(filename))
        root = ET.parse(os.path.join(dir_path, filename)).getroot()

        xml_main = root.find(util.prefix_tag('main'))
        if xml_main is None:
            continue

        title_elem = xml_main.find(util.prefix_tag('title'))
        if title_elem is None:
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

            terms = (util.transform_word(w) for w in word_tokenize(sec_text) if w not in stop_words)
            term_counter = Counter(terms)

            ref_counter = Counter()
            for elem in sec_elem.iter():
                if util.extract_tag(elem.tag) == 'ref':
                    ref_id = elem.attrib.get('href')
                    if not ref_id or not util.is_uscode_id(ref_id):
                        continue
                    ref_id = util.format_section_id(ref_id)
                    ref_counter[ref_id] += 1
                else:
                    matches = itertools.chain.from_iterable(ref_pattern.findall(text) for text in [elem.text, elem.tail] if text)
                    for s, t in matches:
                        s = 's' + s.split('(')[0]
                        t = 't' + t if t else title_id
                        ref_id = (t + '/' + s).lower()
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
