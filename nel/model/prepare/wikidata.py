import gzip
import json

from time import time
from ..data import Store

import logging
log = logging.getLogger()

R_PD_MATCH=')'
L_PD_MATCH=' ('
class BuildWikidataEntityDescriptions(object):
    """ Extracts an entity->short_description store from a wikidata dump """    
    def __init__(self, wikidata_dump_path):
        self.wikidata_dump_path = wikidata_dump_path

    def __call__(self):
        EST_DESC_TOTAL = 2600000 # only used to try and predict runtime
        desc_count = 0

        store = Store.Get('models:descriptions')

        start_time = time()
        with store.batched_inserter(250000) as s:
            with gzip.open(self.wikidata_dump_path, 'r') as gzf:
                for i, line in enumerate(gzf):
                    if i == 50000 or i % 250000 == 0:
                        completed = desc_count / float(EST_DESC_TOTAL)
                        elapsed = time() - start_time
                        if desc_count:
                            eta = ((elapsed / completed)-elapsed) / 60
                        else:
                            eta = 0
                        log.debug('Processed %i objects with %i descriptions, ~%.1f%% done. Eta=%.2fm ...', i, desc_count, completed*100, eta)
                    
                    try:
                        obj = json.loads(line[:-2])
                        entity = obj['sitelinks']['enwiki']['title']
                    except Exception:
                        # json.load will fail on the first and last line of the file
                        # some entities will be missing english descriptions or sitelinks
                        continue

                    description = obj.get('descriptions',{}).get('en',{}).get('value', '')
                    label = obj.get('labels',{}).get('en',{}).get('value', None)

                    if not label or not description:
                        if entity.endswith(R_PD_MATCH):
                            pd_start = entity.rfind(L_PD_MATCH)
                            if pd_start != -1:
                                if not label:
                                    label = entity[:pd_start]
                                if not description:
                                    description = entity[pd_start+len(L_PD_MATCH):-1]
                        if not label:
                            label = entity

                    # instance_of = obj['claims']['P31'][0]['mainsnak']['datavalue']['value']['numeric-id'] 
                    desc_count += 1
                    s.save({
                        '_id': entity.replace(' ','_'),
                        'label': label,
                        'description': description
                    })

        log.info('Done')

    @classmethod
    def add_arguments(cls, p):
        p.add_argument('wikidata_dump_path', metavar='WIKIDATA_DUMP_PATH')
        p.set_defaults(cls=cls)
        return p
