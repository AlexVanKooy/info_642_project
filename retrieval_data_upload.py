import json
import os
import ssl
import requests
from elasticsearch import Elasticsearch
from elasticsearch.connection import create_ssl_context
from requests.auth import HTTPBasicAuth


def get_json_data(filepath):
    with open(filepath,encoding='utf-8') as file_in:
        full_data = json.load(file_in)
    return full_data


def drop_empty_data(j_data, save_file=True):

    """
    lots of fields are not populated and contain the string "No Results" 
    
    This function aims to collect only the populated entries
    """
    # mapped_subset = {}
    plats = list(j_data.keys())
    no_data = "No Results"
    collected_games = {}
    for plat in plats:
        for entry, content in j_data[plat].items():
            if (content != no_data) and (entry not in collected_games.keys()):
                #when the object has data and isn't part of our collection, add it
                collected_games[entry]=content                
            else:
                continue
    
    with open('jdata_minus_empties.json','w') as fout:
        json.dump(collected_games,fout)


def collect_and_set_mapped_fields(j_data, mapped_fields):
    
    final_data = {}
    
    for game in j_data.items():
        temp_dict = {}
        if game[0] not in final_data.keys():
            for field in mapped_fields:
                if game[1][field] != 'Data Not Available':
                    temp_dict[field] = game[1][field]
                else:
                    temp_dict[field] = None
            final_data[game[0]] = temp_dict
        else:
            continue
    return final_data
    
def make_ES_payload(j_data):
    doc_counter = 1
    for entry in j_data.values():
        yield{
            "_index":"av667_info624_202004_project",
            "_type":"document",
            "_id":doc_counter,
            'doc':entry}

                    
            
        

def main():
    context = create_ssl_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    es = Elasticsearch(['tux-es1.cci.drexel.edu','tux-es2.cci.drexel.edu','tux-es3.cci.drexel.edu'],
                       http_auth=('user','secret'), # working on real encrypted passwords
                       scheme="https",
                        port=9200,
                        ssl_context = context)
    
    # print(es.info())
    
                       
    mapped_fields = ["title", "developer","type","description", 
                     "source", "editorial_reviews", "initial_release_date","platforms",
                     "composer","publisher","series"]
    #Already trimmed the file to only have the games with actual data
    # drop_empty_data(game_data, True)
    game_data = get_json_data('jdata_minus_empties.json')
    
    game_data = collect_and_set_mapped_fields(game_data, mapped_fields)
    one_payload = make_ES_payload(game_data)
    print('ready to start uploading?')












if __name__ == '__main__':
    main()
