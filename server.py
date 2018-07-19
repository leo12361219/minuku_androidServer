from flask import Flask, request, jsonify, json
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
import datetime
from datetime import datetime
import dateutil.parser
from bson import json_util
import codecs
import ast
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'LabelingStudy'
app.config['MONGO_URI'] = 'mongodb://localhost/LabelingStudy'

mongo = PyMongo(app)

TripDataKey = ["_id", "device_id", "condition", "createdTime", "startTime", "endTime", "startTimeString", "endTimeString", "sessionid", "annotations"]

@app.route('/')
def test():
    return 'OK'


@app.route('/find_latest_and_insert', methods=['POST'])
def find_latest_and_insert():
    if request.method == 'POST':
        collection = str(request.args['collection'])
        action = str(request.args['action'])

        if collection == 'dump':
            user = mongo.db.dump
        elif collection == 'trip':
            user = mongo.db.trip
        elif collection == 'isAlive':
            user = mongo.db.isAlive
        if action == 'search':
            user_id = request.args['id']
            data = user.find({'device_id': user_id})
            res = data.sort('startTime', -1).limit(1)

            docs = []
            for item in res:
                time = item['startTime']
                docs.append({'startTime': item['startTime']})
            message = json.dumps(docs)
            return message
        
        json_request = request.get_json(force=True, silent=True)
        if action == 'insert' and collection == 'trip':
            # handle the log file: read as string  and store as list to append new data
            #json_request = request.get_json(force=True, silent=True)
            #request_indent = json.dumps(json_request, indent=4, sort_keys=True)
            #content_data.append(request_indent)
            # file = open('insertOrUpdate.txt', 'a')
            # file.write(str(json_request)+'\n')
            # with codecs.open('insertOrUpdate.txt', 'w', 'utf8') as outfile:
            #     for string in content_data:
            #         outfile.write(str(string) + '\n')
            #     outfile.close()
            # handle database
            missing_key = False
            try:
                if '_id' in json_request and 'createdTime' in json_request:
                    data = dict()
                    for key in TripDataKey:
                        if key in json_request and key != '_id':
                            data[key] = json_request[key]
                        elif key not in json_request:
                            print(key, " is missing")
                            missing_key = True
                    if missing_key:
                        file = open('MissingKeyData.txt', 'a')
                        file.write(str(json_request)+'\n')

                    user.update({'_id': json_request['_id']}, {'$set': data}, upsert=True, multi=True)
            except KeyError:
                print ('Key error')
            except Exception as e:
                print (e)
            else:  # if try successfully, then execute else
                print (json_request['createdTime'])
                return json.dumps({'createdTime': json_request['createdTime']})
        elif action=='insert' and collection=='dump':
            try:
                user.insert(json_request)
                return json.dumps({'endTime':json_request['endTime']})
            except Exception as e:
                print (e)
        else:
            #json_request = request.get_json(force=True, silent=True)
            user.insert(json_request)
            return 'insert OK!'


@app.route('/time_interval', methods=['POST'])
def time_interval():
    jsonquery = request.get_json(force=True, silent=True)  # type: unico$
    query = json.loads(jsonquery)
    d_id = query['device_id']
    collection = query['collection']
    start = query['query_start_time']
    end = query['query_end_time']

    if collection == 'dump':
        col = mongo.db.dump
    elif collection == 'trip':
        col = mongo.db.trip
    elif collection == 'isAlive':
        col = mongo.db.isAlive

    json_docs = []
    number = col.find({'device_id': d_id, 'startTime': {'$gte': str(start["$date"])}, 'endTime': {'$lt': str(end["$date"])}}).count()
    in_time_range = col.find({'device_id': d_id, 'startTime': {'$gte': str(start["$date"])}, 'endTime': {'$lt': str(end["$date"])}})
    for doc in in_time_range:
        json_docs.append(doc)
    print (json_docs)
    # search_indent = json.dumps(json_docs, indent=4, sort_keys=True)
    # with codecs.open('search.txt', 'w', 'utf8') as outfile:
    #     outfile.write(search_indent)
    #     outfile.close()
    return json.dumps({'device_id': d_id, "number": number})

if __name__ == '__main__':
    app.run(host="172.31.3.66")