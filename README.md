# Sri lankan Monarchs Search App

This repository contain source code for Sri lankan monarchs search engine created using Python and Elasticsearch. 

</br>

## Repository structure

 ```
├── elastic search                
    ├── bulk_data.ipynb : Code to create the index in elastic search and to upload data
    ├── analyzers
      ├── stopwords.txt : List of stopwords in sinhala language
      ├── synonyms.txt : List of syninyms in sinhala language
├── corpus : Data scaped from Wikipedia
├── app : Source code for the app
    ├── template : 
      ├── index.html: User search interface
    ├── app.py : Falsk based backend of the app
├── query.txt :  Sample queries that can be executed via kibana
├── requirements.txt : list of packages to install
 
 ```
 
 </br>

## Installations

### Installing Elastic Search
1. Download the Elasticsearch archive for your OS: https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html
2. Extract the archive
3. Start Elasticsearch from the  ```bin ``` directory using the command ```elasticsearch```.

### Installing Kibana
1. Download the Elasticsearch archive for your OS: https://www.elastic.co/downloads/kibana
2. Extract the archive
3. Start Kibana from the  ```bin ``` directory using the command ```kibana```.

Note : Kibana is not required for the Search engine app. But for testing more queries that are not initially embedded in the app, you can use kibana. Sample supportable queries are provided in a following section. 


 </br>
 
## Getting started with the Web App

To start the web app run the following commands.

```
git clone https://github.com/AfraHussaindeen/Sri-lankan-monarchs-search-engine.git

cd Sri-lankan-monarchs-search-engine

virtualenv -p python3 env

env\Scripts\activate

pip3 install -r requirements.txt

```
Next, create the index in elastic search by executing each cell in ```bulk_data.ipynb``` notebook and again run the below commands.

```
cd app

flask run
```
Finally , you can access the web app via  http://localhost:5000/.


 </br>
 
## Data 
The [Wikipedia](https://en.wikipedia.org/wiki/List_of_Sri_Lankan_monarchs#Anuradhapura_Kingdom_(437_BC_%E2%80%93_1017_AD)) website was used to gather information about monarchs. Both manual and automated web scraping stratergies were used. For automatic web scraping [Web Scraper - Free Web Scraping](https://chrome.google.com/webstore/detail/web-scraper-free-web-scra/jnhgnonknehpejjnehehllkliplmbmhn?hl=en), chrome extension was used. Below are the considered data fields.

* name
* detail
* spouse
* kingdom
* dynasty
* reign_start
* reign_end
* predecessor
* successor


 </br>
 
## Indexing process

The index was created by defining the settings as follow.

```
# Define the mappings for the elastic search index
Settings = {
    "settings": {
       "index": {
          "number_of_shards": 1,
          "number_of_replicas": 1
       },
       "analysis": {
          "analyzer": { 

            "sin_analyzer": {
                "type": "custom",
                "tokenizer": "icu_tokenizer",
                "char_filter": ["punctuation_filter"],
                "filter": ["sin_stopwords","sin_synonyms", "sin_stemmer" ,"edge_ngram_filter"]
            },
            "sin_search_analyzer" : {
                "type": "custom",
                "tokenizer": "icu_tokenizer",
                "char_filter":["punctuation_filter"], 
                "filter":["sin_stopwords","sin_synonyms", "sin_stemmer"]
            }
         },

         "char_filter": {
            "punctuation_filter":{
               "type":"mapping",
               "mappings":[".=>",":=>","|=>","-=>","_=>","'=>","/=>",",=>"]
            }
         },

         "filter": {
               "edge_ngram_filter": {
                    "type" : "edge_ngram",
                    "min_gram":"3",
                    "max_gram":"20",
                    "side":"front"
               },
               "sin_stemmer": {
                  "type": "hunspell",
                  "locale": "si_LK"
               },
               "sin_stopwords":{
                   "type":"stop",
                   "stopwords_path": "analyzers/stopwords.txt"
               },
               "sin_synonyms":{
                   "type": "synonym",
                   "synonyms_path": "analyzers/synonym.txt"
               }
         }
       }
    },

    "mappings": {
        'properties' : {
        ......
        } 
    }
  
}

```

Here custom analyzers are used with ```icu_tokenizer``` and few other filters such as ```punctuation filter```, ```stop word filter``` , ```synonym filter``` ,  ```sin stemmer``` and etc.
</br>
* ICU_tokenizer 

Tokenizes text into words on word boundaries, as defined in [UAX #29: Unicode Text Segmentation](https://www.unicode.org/reports/tr29/). It behaves much like the standard tokenizer, but adds better support for some Asian languages by using a dictionary-based approach.

* Punctuation filter

Removes a selected set of punctuations that assume to be generally found in user queries. 

* Stop word filter

Used to remove the [stopwords](https://github.com/nlpcuom/Sinhala-Stopword-list) as it doesn't provide any specific meaning to the search in the consuderes context. 

* Synonym filter

Used to reduce the number of varied indexes and hence can boost efficient indexing and searching. 

* Stemmer 

Hunspell - Spell checker and morphological analyzer library is used.

 </br>

## Features

* Text preprocessing 

Use ICU-Tokenizer and few other filters as mentioned above.

* Rule-based classification

A simple rule-based classification is used to identify the intent of the user such as, basic search, exact phrase search, range search and etc.

* Synonym support

A customized analyzer is defined to handle synonyms. "රජ,රජතුමා,නායකයා,නායකතුමා,පාලකයා,නරේන්ද්‍ර,නරපති,මහීපාල,නරදෙව්, භූපති  => රජු" is an example.

* Withstand simple spelling erros.

Úse of wild card queries allow the users to search even if they misspell words. For an example when a user isn't sure what the complete name of a king (ex : සූරතිස්ස ), user can use "සූර*"

* Boosting 

For query optimization a boosting technique is used by assigning a predefined weight for each field.

</br>

## Queries supported (Samples)

*  Match query
```
# Get the details of the monarch restricting the search space to the specified field.
# Raw query : නම : විජය කුමාර

GET monarchs/_search
{
"query":{
  "match" :{
    "name" : "විජය කුමාර"}
  }
}

```
*  Multi match query
```
# Get the records which include any of the terms  in any field.
# Raw query : අභය  පඞුවස්දෙව්

GET monarchs/_search
{
  "query": {
      "multi_match": {
          "query": "අභය  පඞුවස්දෙව්",
          "fields": [
              "name^3",
              "detail^2",
              "spouse^2",
              "kingdom^2",
              "dynasty^2",
              "predecessor",
              "successor"
          ],
      }
  }
}
```
*  Wildcard query
```
# If the exact name of the king is unknown
# Raw query : විජ*

GET monarchs/_search      
{
  "query": {
    "wildcard": {
      "name": {
        "value": "විජ*"
      }
    }
  }
}
```
*  Exact match query
```
# Get the records that have the same phrase in any of the specified field
# Raw query : "වීර පරාක්රම නරේන්ද්රසිංහ"

GET monarchs/_search 
{
  "query": {
    "query_string": {
      "query": "\" වීර පරාක්රම නරේන්ද්රසිංහ\"" ,
      "fields" : [ "name^3", "detail^2", "spouse^2","predecessor","successor","kingdom^2","dynasty^2" ]
    }
  }
}
```
*  Aggregated query
```
# Get the number of monarchs from each kingdom 
# Raw query : "විවිධ රාජධානි වලට අයත් පාලකයන් ගණන"

GET monarchs/_search
{
  "size":0,
  "aggs": {
      "kingdom_filter": {
          "terms": {
              "field": "kingdom.keyword",
              "size":30
            
          }
      }
  }
}
```
*  Range query
```
# Get the monarchs who ruled the country in the specified time period 
# Raw query : "ක්රි.පූ.543 සිට ක්රි.පූ.204 දක්වා පාලකයන්"

GET monarchs/_search   
{
   "query": {
       "range" : {
           "reign_start" : {
               "gte" : -543,
               "lte" :  -204
           }
       }
   }
}
```
*  Boolean query (Initial web app doesn't support this)
```
# Get the monarchs whose name include "විජය" while excluding "රාජසිංහ"

GET monarchs/_search 
{
  "query":{
    "bool":{
      "must":{
        "match":{
          "name": "විජය"
        }
      },
      
      "must_not": {
        "term":{
          "name" : "රාජසිංහ"
        }
      }
      
    }
  }
}
```



### Search results for sample queries

![Capture](https://user-images.githubusercontent.com/47135592/143027374-ac775590-1f60-41a0-946f-e3bfe3a27fca.PNG)

![Capture](https://user-images.githubusercontent.com/47135592/143027882-1668e2b8-a9b9-46ce-8a31-02460277e8a5.PNG)

![Capture](https://user-images.githubusercontent.com/47135592/143028131-e843dc5a-2bdd-4fbd-99f7-f3c60b6355d1.PNG)

![Capture](https://user-images.githubusercontent.com/47135592/143028306-cc77f203-1df7-4c94-80af-17700df8c037.PNG)

![Capture](https://user-images.githubusercontent.com/47135592/143028476-0b1c2ecf-de66-443c-bbda-f9874056ee81.PNG)

![Capture](https://user-images.githubusercontent.com/47135592/143028678-fb27d0b4-7a37-4272-ba8b-0852b0d2d5cb.PNG)


