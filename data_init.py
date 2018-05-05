import sys
import json
import pdb

import pandas as pd
import numpy as np

#from Oracle.db import OracleDatabase
from plastering.metadata_interface import *
from plastering.common import *
from plastering.helper import load_uva_building, load_ucb_building
from plastering.helper import extract_raw_ucb_labels
from jasonhelper import argparser

argparser.add_argument('-b', type=str, dest='building', required=True)


# add raw metadata
args = argparser.parse_args()
building = args.building

if building == 'uva_cse':
    load_uva_building(building)
    print('UVA CSE Done')
    sys.exit()
elif building in ['soda', 'sdh', 'ibm']:
    extract_raw_ucb_labels()
    basedir = './groundtruth/'
    filenames = {
        'soda': basedir + 'SDH-GROUND-TRUTH',
        'sdh': basedir + 'SDH-GROUND-TRUTH',
        'ibm': basedir + 'IBM-GROUND-TRUTH',
    }
    load_ucb_building(building, filenames[building])
    sys.exit()

####################### UCSD ########################
rawdf = pd.read_csv('rawdata/metadata/{0}_rawmetadata.csv'\
                        .format(building), index_col='SourceIdentifier')
for srcid, row in rawdf.iterrows():
    point = RawMetadata.objects(srcid=srcid, building=building)\
                       .upsert_one(srcid=srcid, building=building)
    for k, v in row.items():
        if not isinstance(v, str):
            if np.isnan(v):
                v = ''
        point.metadata[k] = v
    point.save()

print('Finished adding raw metadata')

# add labeled metadata
with open('groundtruth/{0}_full_parsing.json'.format(building), 'r') as fp:
    fullparsings = json.load(fp)
for srcid, fullparsing in fullparsings.items():
    point = LabeledMetadata.objects(srcid=srcid, building=building)\
                           .upsert_one(srcid=srcid, building=building)
    point.fullparsing = fullparsing
    point.save()
print('Finished adding full parsing')

# add tagsets
with open('groundtruth/{0}_tagsets.json'.format(building), 'r') as fp:
    true_tagsets = json.load(fp)
for srcid, tagsets in true_tagsets.items():
    point = LabeledMetadata.objects(srcid=srcid, building=building)\
                           .upsert_one(srcid=srcid, building=building)
    point.tagsets = tagsets
    point.point_tagset = sel_point_tagset(tagsets)
    point.save()

print('Finished adding tagsets')
