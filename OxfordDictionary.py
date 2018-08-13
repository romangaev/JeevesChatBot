# for more information on how to install requests
# http://docs.python-requests.org/en/master/user/install/#install
import requests
import os
# TODO: replace with your own app_id and app_key
app_id = os.environ['OXXX_ID']
app_key = os.environ['OXXX_KEY']
language = 'en'


def oxford_dic_request(word_id):
    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/'  + language + '/'  + word_id.lower()
    r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key})
    # print("code {}\n".format(r.status_code))
    print("text \n" + r.text)
    # print("json \n" + json.dumps(r.json()))
    oxford_dict=r.json()
    response=""
    for i in oxford_dict["results"]:
        # print(word_id)
        # print(i["lexicalEntries"][0]["pronunciations"][0]["phoneticSpelling"])
        response += word_id
        response += '\n'
        response += i["lexicalEntries"][0]["pronunciations"][0]["phoneticSpelling"]
        def_counter = 1
        for j in i["lexicalEntries"]:
            # print(j["lexicalCategory"])
            response += '\n'
            response +=str(def_counter)+"."+ j["lexicalCategory"]
            def_counter += 1
            for k in j["entries"]:

                for v in k["senses"]:
                    for w in v["definitions"]:
                        # print("\t "+str(def_counter)+": "+w)
                        response += '\n'
                        response += "\t - "+w

                        if "examples" in v:
                            for s in v["examples"]:
                            #    print('\t\tExample: '+str(w["text"]))
                                response += '\n'
                                response+= '\t\tExample: '+str(s["text"])
    return response
