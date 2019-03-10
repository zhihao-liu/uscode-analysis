import uscode
import boolean

usc = uscode.USCode('./data/uscode/')

# x = usc.find_section_by_id('1', '1')
# print(x)

# x = usc.search_sections_fulltext('bilateral and multilateral')
# print([k.identifier[len('/us/usc/'):] for k in x if k.identifier])

x = usc.search_all_sections_boolean('copyright AND is AND NOT legal')
for k in x:
    print("title: %s \tsection:%s" % (k.title_id, k.section_id))