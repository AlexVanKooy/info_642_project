import json
import os
import ssl
import keyring
import requests
from dateutil import parser
from elasticsearch import Elasticsearch, helpers
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


def collect_and_set_mapped_fields(j_data, mapped_fields, write_to_file=False):
    
    final_data = {}
    
    for game in j_data.items():
        temp_dict = {}
        if game[0] not in final_data.keys():
            for field in mapped_fields:
                if game[1][field] != 'Data Not Available':
                    if field == "initial_release_date":
                        temp_date = parser.parse(game[1][field])
                        temp_dict[field] = str(temp_date.date())
                    else:
                        temp_dict[field] = game[1][field]
                else:
                    temp_dict[field] = None
            final_data[game[0]] = temp_dict
        else:
            continue
    if write_to_file == True:
        with open("final_data_payload.json","w") as data_out:
            json.dump(final_data,data_out)
    return final_data
    
def make_ES_payload(j_data, target_index):
    doc_counter = 0
    doc_list = []
    for entry in j_data.values():
        doc_counter+=1

        item = [{"index":{"_index":target_index,"_id":doc_counter}},
                entry]
        doc_list.extend(item)
    return doc_list

                    
                    
def build_actions(j_data, target_index):
    
    actions = [
    {
        '_index': target_index,
        # '_type': 'document',
        '_id': i,
        '_source': v,
    }
    for i, (k, v) in enumerate(j_data.items(), 1)
    ]
    return actions         
        

def main():
    context = create_ssl_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    es = Elasticsearch(['tux-es1.cci.drexel.edu','tux-es2.cci.drexel.edu','tux-es3.cci.drexel.edu'],
                       http_auth=('av667',keyring.get_password('elastic',"av667")), # working on real encrypted passwords
                       scheme="https",
                        port=9200,
                        ssl_context = context,
                        timeout=30, max_retries=10, retry_on_timeout=True)
    
    
    
                       
    mapped_fields = ["title", "developer","type","description", 
                     "source", "editorial_reviews", "initial_release_date","platforms",
                     "composer","publisher","series"]
    
    ###############
    # If you do not have the "jdata_minus_empties.json" file yet and have the original data, run the following
    ########
    # drop_empty_data(game_data, True)
    
    game_data = get_json_data('jdata_minus_empties.json')
    
    game_data = collect_and_set_mapped_fields(game_data, mapped_fields, True)
    
    actions = build_actions(game_data, target_index="av667_info624_202004_project_no_doc_prefix")
    
    
    try:
        stats=helpers.bulk(es,actions)
        # es.bulk(actions)
    except Exception as e:
        print("something broke")
        print(e)
    












if __name__ == '__main__':
    main()
