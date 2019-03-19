import sys
import boolean
import logging

from uscode import USCode
from citation_network import CitationNetwork


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

usc = USCode('./data/uscode/')

# option = sys.argv[1]
# if option == 'section':
#     title_id, section_id = sys.argv[2:4]
#     section = usc.find_section(title_id, section_id)
#     print(section.to_string() if section else "Not found.")

# elif option in ['fulltext', 'boolean']:
#     search = usc.search_all_fulltext if option == 'fulltext' else usc.search_all_boolean
#     results = search(sys.argv[2])
#     for section in results:
#         if section.location:
#             print("title: %s\tsection: %s" % section.identifier)

cn = CitationNetwork(usc)
