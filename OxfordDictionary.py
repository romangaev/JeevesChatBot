# for more information on how to install requests
# http://docs.python-requests.org/en/master/user/install/#install
import requests
import os
# TODO: replace with your own app_id and app_key
app_id = os.environ['OXXX_ID']
app_key = os.environ['OXXX_KEY']
language = 'en'


def oxford_dic_request(word_id):
    response = ""
    audio_url = ""
    examples = ""
    audio_url_check_any = False
    examples_check_any = False

    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/'  + language + '/'  + word_id.lower()
    r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key})
    print("Oxford status code:")
    print("code {}\n".format(r.status_code))
    if r.status_code == '200' or r.status_code == 200:
        print("text \n" + r.text)
        # print("json \n" + json.dumps(r.json()))
        oxford_dict = r.json()

        for i in oxford_dict["results"]:
                # print(word_id)
                # print(i["lexicalEntries"][0]["pronunciations"][0]["phoneticSpelling"])
                response += '*'+word_id.capitalize()+'*'

                if "pronunciations" in i["lexicalEntries"][0] and "phoneticSpelling" in i["lexicalEntries"][0]["pronunciations"][0]:
                    response += '\n'
                    response += i["lexicalEntries"][0]["pronunciations"][0]["phoneticSpelling"]
                def_counter = 1


                for j in i["lexicalEntries"]:
                    # print(j["lexicalCategory"])
                    response += '\n\n'
                    response += str(def_counter)+". "+ j["lexicalCategory"]
                    examples += j["lexicalCategory"]
                    examples += '\n'
                    def_counter += 1
                    def_stopper = 1
                    examples_counter = 1
                    if "pronunciations" in j:
                        if "audioFile" in j["pronunciations"][0]:
                            audio_url = j["pronunciations"][0]["audioFile"]
                            audio_url_check_any=True
                    for k in j["entries"]:

                        for v in k["senses"]:
                            if "definitions" in v:
                                for w in v["definitions"]:
                                    if def_stopper >3:
                                        break
                                    # print("\t "+str(def_counter)+": "+w)
                                    response += '\n'
                                    response += "- "+w
                                    def_stopper += 1

                            if "examples" in v:
                                examples_check_any=True
                                for s in v["examples"]:
                                #    print('\t\tExample: '+str(w["text"]))
                                    if examples_counter>5:
                                        break
                                    examples += str(examples_counter)+'. '+str(s["text"])
                                    examples += '\n'
                                    examples_counter +=1

        if not examples_check_any:
            examples = "Couldn't find any examples"
        if not audio_url_check_any:
            audio_url = "Couldn't find any audio"

        return {"text": response, "attachment": audio_url, "examples": examples}
    else:
        return {"text": "I don't know this word", "attachment": None, "examples": None}


def oxford_dic_syn_ant(word_id):
    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower() + '/synonyms;antonyms'
    synonyms = "Synonyms:\n"
    antonyms = "Antonyms:\n"
    r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})

    if r.status_code == '200' or r.status_code == 200:
        oxford_dict = r.json()

        for i in oxford_dict["results"]:
            # print(word_id)
            # print(i["lexicalEntries"][0]["pronunciations"][0]["phoneticSpelling"])
            syn_counter = 1
            ant_counter = 1
            for j in i["lexicalEntries"]:
                # print(j["lexicalCategory"])

                for k in j["entries"]:
                    for v in k["senses"]:
                        if "antonyms" in v:
                            for w in v["antonyms"]:
                                if ant_counter>5:
                                    break
                                antonyms += str(ant_counter)+". "+w["id"]+"\n"
                                ant_counter +=1

                        if "synonyms" in v:
                            for x in v["synonyms"]:
                                if syn_counter>5:
                                    break
                                synonyms += str(syn_counter) + ". " + x["id"]+"\n"
                                syn_counter += 1

    if antonyms == "Antonyms:\n":
         antonyms = "...And don't think there are any antonyms"
    if synonyms == "Synonyms:\n":
        synonyms = "Well..As for synonyms, I couldn't find anything related"

    return {"synonyms": synonyms, "antonyms": antonyms}