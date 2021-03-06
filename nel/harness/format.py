import json
from re import findall, match, DOTALL

markdown_characters = u"\\`*_{}[]()#+-.!"

def normalize_special_characters(text):
    """Replace special unicode characters in text"""
    entities = {
        u'\u00A0': ' ',
        u'&quot;': '"     ',
        u'\u0022': '"',
        u'\u00AB': '"',
        u'\u00BB': '"',
        u'\u02BA': '"',
        u'\u02DD': '"',
        u'\u030B': '"',
        u'\u030E': '"',
        u'\u05F4': '"',
        u'\u201C': '"',
        u'\u201D': '"',
        u'\u2036': '"',
        u'\u2033': '"',
        u'\u275D': '"',
        u'\u275E': '"',
        u'\u3003': '"',
        u'\u301D': '"',
        u'\u301E': '"',
        u'\U0001F676': '"',
        u'\U0001F677': '"',
    }
    for c, r in entities.iteritems():
        if c in text:
            text = text.replace(c, r)
    return text

def markdown_to_whitespace(markdown_txt):
    """Convert a text from markdown whitespace padded unicode."""
    resu = u''

    # remove table
    match_table = findall(ur'(<table>.+?</table>)', markdown_txt, DOTALL)
    for match_t in match_table:
        markdown_txt = markdown_txt.replace(match_t, u' ' * len(match_t))
        
    for line in markdown_txt.split('\n'):
        if len(line) > 0:
            # remove blockquote formatting
            if line.startswith(u'> '):
                line = u'  ' + line[2:]

            # remove headline formatting
            match_head = match(ur'^(#+) (.+)$', line)
            if match_head:
                sz = len(match_head.groups()[0])
                if sz < 7:
                    line = (' ' * sz) + line[sz:]

            # remove emphasized formatting
            emphs = findall(ur'((?<!\\)\*(.+?)(?<!\\)\*)', line)
            for emph in emphs:
                line = line.replace(emph[0], emph[0].replace('*', ' '))

            # remove important formatting
            imps = findall(ur'((?<!\\)__(.+?)(?<!\\)__)', line)
            for imp in imps:
                line = line.replace(imp[0], imp[0].replace('_', ' '))

            # remove link formatting
            links_txt = u''
            links = findall(ur'((?<!\\)\[(.+?)(?<!\\)\](?<!\\)(\(\S+(?<!\\)\)))', line)
            for link in links:
                line = line.replace(link[0], ' ' + link[1] + ' ' + (' ' * len(link[2])))
                links_txt = links_txt + link[1]

            # remove extra backslash
            for char in markdown_characters:
                line = line.replace(u"\\" + char, " " + char)
            
            # add the text if it contains more than a link
            resu += line + u'\n'

    # remove special unicode characters
    return normalize_special_characters(resu)

def to_neleval(doc):
    default_probability = 1.0
    default_type = 'UNK'
    return u'\n'.join(
        u'\t'.join([
            doc.id, 
            str(m.begin), 
            str(m.end), 
            '' if chain.resolution == None else chain.resolution.id,
            str(default_probability),
            default_type]) 
        for chain in doc.chains for m in chain.mentions)

def to_json(doc):
    return json.dumps({
        'id':doc.id,
        'mentions':[{
            'begin': m.begin,
            'length': len(m.text),
            'text': m.text,
            'resolution': None if chain.resolution == None else {
                'entity': chain.resolution.id,
                'features': chain.resolution.features
            }
        } for chain in doc.chains for m in chain.mentions]})
