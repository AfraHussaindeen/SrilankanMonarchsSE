import flask
from flask import *
from flask_cors import CORS, cross_origin
from elasticsearch import Elasticsearch

# Create an instance of the elastic search
index_name = 'monarchs'
es = Elasticsearch('localhost', port=9200)


def termSearch(search_term, limit=15):
    """
    Performs a basic search .
    Uses multi-match.
    Here certain fields are boosted (^) to give more weight for selected fields.
    """

    res = es.search(
        index=index_name,
        size=limit,
        body={
            'query': {
                'multi_match': {
                    'query': search_term,
                    'fields': [
                        "name^4",
                        "detail^2",
                        "spouse^2",
                        "kingdom^3",
                        "dynasty^3",
                        "predecessor",
                        "successor"
                    ]
                }
            },
            "aggs": {
                "kingdom_filter": {
                    "terms": {
                        "field": "kingdom.keyword",
                        "size": 5
                    }
                },
                "dynasty_filter": {
                    "terms": {
                        "field": "dynasty.keyword",
                        "size": 5
                    }
                }
            }
        }
    )

    return res


def phraseSearch(search_phrase, limit=15):
    """
    Performs an exact phrase search .
    Here certain fields are boosted (^) to give more weight for selected fields.
    """
    res = es.search(
        index=index_name,
        size=limit,
        body={
            "query": {
                "query_string": {
                    "query": "\"" + search_phrase + "\"",
                    "fields": [
                        "name^3",
                        "detail^2",
                        "spouse^2",
                        "predecessor",
                        "successor",
                        "kingdom^2",
                        "dynasty^2"]
                }
            }
        })

    return res


def keywordSearch(keyword, search_text, limit=15):
    """
    Performs search  based on a specified field.
    """
    res = es.search(
        index=index_name,
        size=limit,
        body={
            'query': {
                'match': {
                    keyword: search_text,
                }
            }
        }

    )

    return res


def rangeSearch(start, end, limit=200):
    """
    Performs a range query search to extract the monarchs ruled in the specified time period
    """

    res = es.search(
        index=index_name,
        size=limit,
        body={
            "query": {
                "range": {
                    "reign_start": {
                        "gte": start,
                        "lte":  end
                    }
                }
            }
        }


    )

    return res


def aggregationQuery(field="kingdom"):

    if (field == "kingdom"):
        query_body = {
            "size": 0,
            "aggs": {
                "filter": {
                    "terms": {
                        "field": "kingdom.keyword",
                        "size": 30

                    }
                }
            }
        }
    if (field == "dynasty"):
        query_body = {
            "size": 0,
            "aggs": {
                "filter": {
                    "terms": {
                        "field": "dynasty.keyword",
                        "size": 30

                    }
                }
            }
        }

    res = es.search(
        index=index_name,
        body=query_body)

    return res


def getSearchType(query):
    """
    Identifies and return the type of search to be performed for a given query
    """
    query = query.strip()

    mappings = {
        "නම": "name",
        "විස්තර": "detail",
        "කලත්‍රයා": "spouse",
        "රාජධානිය": "kingdom",
        "රාජවංශය": "dynasty",
        "රාජ්‍ය සමයේ ආරම්භය": "reign_start",
        "රාජ්‍ය සමයේ අවසානය": "reign_end",
        "පූර්වප්‍රාප්තිකයා": "predecessor",
        "අනුප්‍රාප්තිකයා": "successor"

    }

    # Check for phrase query
    if (query[0] == '"' and query[-1] == '"'):
        return {"type": "phraseSearch", "query": {"key": None, "value": query.strip('"')}}

    # Check for field name specified query
    if (':' in query):

        key, value = query.strip().split(':')
        key = key.strip()
        value = value.strip()

        if (key in mappings.keys()):
            return {"type": "keywordSearch", "query": {"key": mappings[key], "value": value}}
        else:
            return {"type": "termSearch", "query": {"key": None, "value": query}}

    # Check for range query
    if ('සිට' in query and 'දක්වා' in query):
        text = query.replace("ක්රි.පූ.", "-")
        text = text.replace("ක්රි.ව.", "")
        text = text.strip().split(" ")
        from_index = text.index('සිට')-1
        to_index = text.index('දක්වා')-1

        from_date = eval(text[from_index])
        to_date = eval(text[to_index])

        return {"type": "rangeSearch", "query": {"key": None, "value": query, "range": [from_date, to_date]}}

    # Check for aggregation query
    agg_words = ['ගණන', 'ගනන']

    for agg_word in agg_words:
        if (agg_word in query):
            if ('රාජධා' in query):
                return {"type": "aggregationQuery", "query": {"key": "kingdom", "value": None}}
            if ('රාජවංශ' in query):
                return {"type": "aggregationQuery", "query": {"key": "dynasty", "value": None}}

    return {"type": "termSearch", "query": {"key": None, "value": query}}


def text_postprocessing(responses):
    processed_responses = []
    mappings = {
        "name": "නම",
        "detail": "විස්තර",
        "spouse": "කලත්රයා",
        "kingdom": "රාජධානිය",
        "dynasty": "රාජවංශය",
        "reign_start": "රාජ්ය සමයේ ආරම්භය",
        "reign_end": "රාජ්ය සමයේ අවසානය",
        "predecessor": "පූර්වප්රාප්තිකයා'",
        "successor": "අනුප්රාප්තිකයා'"

    }

    for response in (responses):
        response = response['_source']
        processed_response = {}
        for key in response.keys():
            value = response[key]
            if (key == "reign_start" or key == "reign_end"):
                if (value != "" and value < 0):
                    value = "ක්රි.පූ. "+str(-value)
                elif (value != "" and value > 0):
                    value = "ක්රි.ව. "+str(value)
            processed_response[mappings[key]] = value

        processed_responses.append(processed_response)

    return processed_responses


# Define the flask app
app = flask.Flask(__name__, template_folder='./template')
app.config['SECRET_KEY'] = 'lolipop'
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/*": {"origins": "http://localhost:5000"}})


@app.route('/')
def home():
    return render_template('index.html', content={"query": "", "records": []}, is_agg=False)


@app.route('/search', methods=['POST'])
def serve():
    # Get the query
    query_text = flask.request.form['query']

    # Identify the type of search user intended to perform
    result = getSearchType(query_text)
    type, query = result['type'], result['query']
    # If the user wanted to find the records with the exact phrase included,
    if (type == 'phraseSearch'):
        response = phraseSearch(query['value'])

    # If the user wanted to find records with given term in the user specified field,
    if (type == 'keywordSearch'):
        response = keywordSearch(query['key'], query['value'])

    # If the user want to find the records of monarchs who rule the country in the user specified time period,
    if (type == 'rangeSearch'):
        response = rangeSearch(query['range'][0], query['range'][1])

    if (type == 'aggregationQuery'):
        response = aggregationQuery(query['key'])

        return render_template('index.html', content={"query": query_text, "records": response['aggregations']['filter']['buckets']}, is_agg=True)

    if (type == 'termSearch'):
        response = termSearch(flask.request.form['query'])

    # Extract the resulted records
    responses = response['hits']['hits']
    # Postprocess the records for a fixed structure
    responses = text_postprocessing(responses)

    return render_template('index.html', content={"query": query_text, "records": responses}, is_agg=False)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000')
