#!/usr/bin/env python
from .process import Process
from ..util import spanset_insert

import logging
log = logging.getLogger()

class FeatureRankResolver(Process):
    def __init__(self, feature):
        self.feature = feature
    
    def __call__(self, doc):
        for m in doc.chains:
            if m.candidates:
                m.resolution = sorted(m.candidates, key=lambda c: c.features[self.feature], reverse=True)[0] 
            else:
                m.resolution = None
        return doc

class GreedyOverlapResolver(Process):
    def __init__(self, feature):
        self.feature = feature

    def __call__(self, doc):
        """ Resolve overlapping mentions by taking the highest scoring mention span """
        # tracks set of disjoint mention spans in the document
        span_indicies = []

        non_nils = (m for m in doc.chains if m.resolution)
        nils = (m for m in doc.chains if not m.resolution)

        for chain in sorted(non_nils, key=lambda ch: ch.resolution.features[self.feature], reverse=True):
            mentions = []
            for m in sorted(chain.mentions,key=lambda m:len(m.text),reverse=True):
                # only resolve this link if its mention span doesn't overlap with a previous insert
                if spanset_insert(span_indicies, m.begin, m.end - 1):
                    mentions.append(m)
            chain.mentions = mentions

        for chain in nils:
            mentions = []
            for m in sorted(chain.mentions, key=lambda m: len(m.text), reverse=True):
                if spanset_insert(span_indicies, m.begin, m.end - 1):
                    mentions.append(m)
            chain.mentions = mentions

        return doc
