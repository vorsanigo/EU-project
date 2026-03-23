'''
Main to perform geocoding, choosing between "only Nominatim" and "Nominatim + NER"
'''

import argparse
import os
import json
from nominatim_ner_geocoding import *


parser = argparse.ArgumentParser(description='Locations extraction and geocoding')
parser.add_argument('-operation_type',
                    type=str,
                    default='nominatim',
                    help='Operation type')
parser.add_argument('-data',
                    type=str,
                    help='Dataset path')
parser.add_argument('-loc_field',
                    type=str,
                    default='location',
                    help='Location field')
parser.add_argument('-user_field',
                    type=str,
                    default='author_id',
                    help='user field')
parser.add_argument('-lang_field',
                    type=str,
                    default='lang',
                    help='Language field')
parser.add_argument('-italy_world',
                    type=str,
                    default=False,
                    help='False for world - True for Italy')
parser.add_argument('-org',
                    type=str,
                    default=False,
                    help='True for org - False for not org')
parser.add_argument('-threshold',
                    type=float,
                    default=0,
                    help='Threshold on Nominatim results')
parser.add_argument('-output',
                    type=str,
                    default='output.csv',
                    help='Output file')


args = parser.parse_args()

geocoder = NominatimLocGeocoder()


# flags and weirds words files
flags = 'unicode_flags.csv'
words = 'weird words.csv'
file_flags = os.path.join(os.getcwd(), flags)
file_words = os.path.join(os.getcwd(), words)

# corenlp and stanza languages files
corenlp_file = 'lang_coreNLP.json'
stanza_file = 'lang_stanza.json'
lang_corenlp_file = os.path.join(os.getcwd(), corenlp_file)
lang_stanza_file = os.path.join(os.getcwd(), stanza_file)



# only nominatim -> we use function that writes on csv step by step
if args.operation_type == 'nominatim':
    print(args.data)
    df = pd.read_csv(args.data)

    geocoder.find_tot_loc_nominatim_pipeline_csv(df, args.loc_field, args.user_field, file_flags, file_words,
                                                 args.italy_world, args.output)



# nominatim + ner + nominatim -> we use function that writes on csv step by step
elif args.operation_type == 'nominatim_ner':
    
    df = pd.read_csv(args.data)

    with open(lang_corenlp_file) as corenlp:
        lang_corenlp = json.load(corenlp)
    with open(lang_stanza_file) as stanza:
        lang_stanza = json.load(stanza)

    geocoder.find_tot_loc_nominatim_ner_pipeline_csv(df, args.loc_field, args.user_field, args.lang_field, file_flags,
                                                     file_words, args.threshold, lang_corenlp, lang_stanza, args.org,
                                                     args.italy_world, args.output)