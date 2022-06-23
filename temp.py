from pymongo import MongoClient,ReadPreference
import urllib
import ssl

username=urllib.parse.quote_plus("nhannt70")
password=urllib.parse.quote_plus("Kosnhan123")
port=27017
host='localhost'

#host=f"sample-documentdb.cluster-cggedtero1ay.us-west-2.docdb.amazonaws.com:{port}"
#dbName="general"


# dbUri = f'mongodb://{username}:{password}@{host}:{port}/?tls=true&tlsCAFile=./rds-combined-ca-bundle.pem&retryWrites=false&tlsAllowInvalidHostnames=true'
dbUri = f'mongodb://{username}:{password}@{host}:{port}/?ssl=true&sslCAFile=./rds-combined-ca-bundle.pem&sslAllowInvalidHostnames=true'

# dbUri = f'mongodb://{username}:{password}@{host}/?tls=true&tlsCAFile=./rds-combined-ca-bundle.pem&retryWrites=false'
print(dbUri)

client = MongoClient(dbUri, ssl_cert_reqs=ssl.CERT_NONE)
mongodb = client['x_ray']
mongocol = mongodb['x_ray_collection_8']
results = mongocol.find({}, {'img_id': 1, '_id':0})
imgs_id = []
for i in list(results):
    print(i)
    if len(i) == 0:
        continue
    else:
        imgs_id.append(i['img_id'])
print(imgs_id)
# imgs_id = [i['img_id'] for i in list(results)]
# print(list(results))
