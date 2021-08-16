import json
import os
from elasticsearch import Elasticsearch
import requests
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
    for entry in j_data.values():
        yield{
            "_index":"av667_info624_202004_project"
        }

                    
            
        

def main():
    es = Elasticsearch({"host":"tux-es1.cci.drexel.edu",
                        "port":9200})
    
    
                       
    mapped_fields = ["title", "developer","type","description", 
                     "source", "editorial_reviews", "initial_release_date","platforms",
                     "composer","publisher","series"]
    #Already trimmed the file to only have the games with actual data
    game_data = get_json_data('jdata_minus_empties.json')
    # drop_empty_data(game_data, True)
    game_data = collect_and_set_mapped_fields(game_data, mapped_fields)
    print('ready to start uploading?')
    
# es.get(index="av667_info624_202004_articles",id=16)










if __name__ == '__main__':
    main()
