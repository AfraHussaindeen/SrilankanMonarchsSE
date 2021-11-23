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

Wikipedia [Wikipedia](https://en.wikipedia.org/wiki/List_of_Sri_Lankan_monarchs#Anuradhapura_Kingdom_(437_BC_%E2%80%93_1017_AD))  was used to collect informations of 189 monarchs. Both manual and automated web scraping stratergies were used. For automatic web scraping [Web Scraper - Free Web Scraping](https://chrome.google.com/webstore/detail/web-scraper-free-web-scra/jnhgnonknehpejjnehehllkliplmbmhn?hl=en), chrome extension was used. 

Considered data fields are : 
* name (stritextng)
* detail (text)
* spouse (text)
* kingdom (text)
* dynasty (text)
* reign_start (number)
* reign_end (number)
* predecessor (text)
* successor (text)


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
Seperate custom analyzers are  used each for indexing time and querying time. Both custom analyzers comprised of,

* <b>ICU-tokenizer</b> - Behaves much like a standard tokenizer, buts adds better support for Asian languages.
* <b>Punctuation filter</b> - Removes a selected set of punctuations that assume to be generally found in user queries.
* <b>Stopword filter</b> - Removes the [stopwords](https://github.com/nlpcuom/Sinhala-Stopword-list) as it doesn’t provide any specific meaning to the search in the considered context
* <b>Synonym filter</b> - Reduce the number of varied indexed and as a result boost efficient indexing and searching
* <b>Stemmer</b> - Provides the stems of the word. Hunspell - spell checker was used.

Apart from the above components, “Edge n-gram filter” is used for indexing analyzers. This filter is generally used to support search-as-you-type queries. But the initially implemented web app is not designed to support this.

 </br>

## Features

* <b>Text preprocessing</b>  - ICU-tokenizer and a few other filters as mentioned above are used
* <b>Rule-based classification</b>  - Used to identify the user intent such as , basic search, range search, etc.
* <b>Synonym support</b>  - Used to handle synonyms such as "රජ,රජතුමා,නායකයා,නායකතුමා,පාලකයා,නරේන්ද්‍ර,නරපති,මහීපාල,නරදෙව්, භූපති  => රජු" 
* <b>Withstand simple spelling erros </b> - Úse wild card queries allow the users to search even if they misspell words. For an example when a user isn't sure what the complete name of a king (ex : සූරතිස්ස ), user can use "සූර*"
* <b>Boosting </b> - Used for query optimization by assigning a predefined weight for each field.

</br>

## Queries supported (Samples)

*  Match query
Used to search by the name of the monarch, spouse, kingdom, dynasty, predecessor, and successor specifying the field name (ex => නම : විජය කුමාර )

```
GET monarchs/_search
{
"query":{
  "match" :{
    "name" : "විජය කුමාර"}
  }
}

```

*  Multi match query
Used to search by terms where the  term can be in any of the specified set of fields. (ex=> අභය  පඞුවස්දෙව් )
```

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
Used to search the details when the exact name of the king is unknown.
```

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
Used to search by a fixed phrase where the phrase can be in any of the specified set of fields (ex => “වීර පරාක්රම නරේන්ද්රසිංහ” )

```


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
Used to get the number of monarchs when grouped by the kingdom and dynasty (ex => විවිධ රාජධානි වලට අයත් පාලකයන් ගණන )

```
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
Used to extract the monarchs who ruled the kingdom in the specified time (ex => ක්රි.පූ.543 සිට ක්රි.පූ.204 දක්වා පාලකයන්)
```

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


