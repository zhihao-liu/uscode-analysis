from os import path
import sys
import xml.etree.ElementTree as ET


ns_prefix = '{http://xml.house.gov/schemas/uslm/1.0}'
new_line_tags = {'section', 'subsection', 'paragraph', 'subparagraph', 'clause', 'subclause'}
xml_folder = '/users/zhihaoliu/desktop/uscode/xml'


def prefix(tag):
    return ns_prefix + tag


def deprefix(tag):
    return tag[len(ns_prefix):]


def is_new_line(tag):
    return deprefix(tag) in new_line_tags


def find_section(title, section):
    file_path = path.join(xml_folder, 'usc%s.xml' % title)
    tree = ET.parse(file_path)
    root = tree.getroot()

    str_builder = []
    elem = root.find('.//%s[@identifier="/us/usc/t%s/s%s"]' % (prefix('section'), title, section))
    for c in elem.iter():
        if str_builder and is_new_line(c.tag):
            str_builder.append('\n')
        if c.text:
            str_builder.append(c.text)
            str_builder.append(' ')

    return ''.join(str_builder)



title = sys.argv[1]
section = sys.argv[2]

content = find_section(title, section)
print(content)
