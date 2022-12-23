import psycopg2
import json
db = psycopg2.connect(
	host="127.0.0.1",
	database="pdt_database_new",
	user="postgres",
	password="juhbte1",
	port="5432"
)
dataTweets = {
				"properties":{
				"authors":[]
}}
authorsBluep = {
      			"id": -1,
          		"name": "NULL" ,
          		"username": "NULL" ,
          		"description": "NULL" ,
          		"followers_count": -1 ,
          		"following_count":  -1,
          		"tweet_count":  -1,
          		"listed_count":  -1,
				}

conversationsBluep = {
				"id":  -1,
                "author_id": -1,
            	"content":  "NULL",
              	"possibly_sensitive":  "NULL",
              	"language":  "NULL",
              	"source":  "NULL",
              	"retweet_count":  -1,
              	"reply_count":  -1,
              	"like_count":  -1,
              	"quote_count":  -1,
              	"created_at":  "NULL",
              	"author": [],
			  	"conversation_references" : [],
			  	"links" : [],
			 	 "annotations" : [],
			  	"context_domains" : [],
			  	"context_entities" : [],
			  	"hashtags" : []




				 }
conversation_referencesBluep = {
				"id": -1,
                "conversaton_id": -1,
				"parent_id":-1,
                "type":  "NULL",
                "parent": []
}
reducedAuthor = {
				"id": -1,
				"name": "NULL",
                "description": "NULL"
}
parentBluep = {
				"id": "NULL",
                "content": "NULL",
                "hashtags": [],
                "author": []
              }



linksBluep = {
		"id": -1,
		"conversation_id": -1,
		"url": "NULL",
		"title": "NULL",
		"description": "NULL"


}

annotationsBluep = {
		"id": -1,
        "conversation_id": -1,
        "value":  "NULL",
        "type":  "NULL",
        "probability": -1


}

context_domainsBluep = {
	"id": -1,
	"name": "NULL",
	"description": "NULL"

}

context_entitiesBluep = {

	"id": -1,
	"name": "NULL",
	"description": "NULL"

}

hashtagsBluep = {

	"id": "NULL",
	"tag": "NULL"

}
def getField(cur, dict):
	data = cur.fetchall()
	arrayDict = []
	for row in data:
		for fieldCount, key in enumerate(dict):
			if key == "probability":
				dict[key] = float(row[fieldCount])
			else:
				dict[key] = row[fieldCount]
		arrayDict.append(dict)
	return arrayDict

def getFieldAuthor(cur, dict):
	data = cur.fetchone()
	arrayDict = []
	for fieldCount, key in enumerate(dict):
		if key == "probability":
			dict[key] = float(data[fieldCount])
		else:
			dict[key] = data[fieldCount]
	arrayDict.append(dict)
	return arrayDict


cur = db.cursor()
offset = 0

tweets_counter = 0
while (True):
	cur.execute("SELECT * FROM zadanie1.conversations LIMIT 1 OFFSET {}".format(offset))
	data = cur.fetchone()
	length = len(data)
	conversations = conversationsBluep.copy()
	conversations['author'] = []
	conversations['conversation_references'] = []
	conversations['links'] = []
	conversations['annotations'] = []
	conversations['context_domains'] = []
	conversations['context_entities'] = []
	conversations['hashtags'] = []
	for fieldCount, key in enumerate(conversations):
		if key == "created_at":
			conversations[key] = str(data[fieldCount])
		else:
			conversations[key] = data[fieldCount]

		if length - 1== fieldCount:
			break
	cur.execute("select * from zadanie1.authors WHERE id={}".format(conversations['author_id']))
	authors = authorsBluep.copy()
	conversations['author'] = getFieldAuthor(cur, authors)
	cur.execute("select * from zadanie1.conversation_references WHERE conversation_id={}".format(conversations['id']))
	data = cur.fetchall()
	for row in data:
		length = len(row)
		conversation_references = conversation_referencesBluep.copy()
		conversation_references["parent"] = []
		for fieldCount, key in enumerate(conversation_references):
			conversation_references[key] = row[fieldCount]
			if length - 1 == fieldCount:
				cur.execute(
					"SELECT * FROM zadanie1.conversations WHERE id={}".format(conversation_references["parent_id"]))
				dataInner = cur.fetchone()
				parent = parentBluep.copy()
				parent["hashtags"] = []
				parent["author"] = []

				parent["id"] = dataInner[0]
				parent["content"] = dataInner[2]

				cur.execute("select * from zadanie1.authors WHERE id={}".format(dataInner[1]))
				dataInnerAuthor = cur.fetchone()
				authorRed = reducedAuthor.copy()
				authorRed["id"] = dataInnerAuthor[0]
				authorRed["name"] = dataInnerAuthor[1]
				authorRed["description"] = dataInnerAuthor[3]
				parent["author"].append(authorRed)
				cur.execute("select hashtag_id from zadanie1.conversation_hashtags WHERE conversation_id={}".format(
					parent["id"]))
				hashtagId = cur.fetchall()
				for id in hashtagId:
					cur.execute("select * from zadanie1.hashtags WHERE id={}".format(id[0]))
					hashtags = hashtagsBluep.copy()
					parent['hashtags'] = getField(cur, hashtags)
				conversation_references["parent"].append(parent)
				conversations["conversation_references"].append(conversation_references)
				break
	cur.execute("select * from zadanie1.links WHERE conversation_id={}".format(
		conversations['id']))
	links = linksBluep.copy()
	conversations['links'] = getField(cur, links)
	cur.execute("select * from zadanie1.annotations WHERE conversation_id={}".format(
		conversations['id']))
	annotations = annotationsBluep.copy()
	conversations['annotations'] = getField(cur, annotations)

	cur.execute("select * from zadanie1.context_annotations WHERE conversation_id={}".format(
		conversations['id']))
	entitiesDomains = cur.fetchall()
	for row in entitiesDomains:
		cur.execute("select * from zadanie1.context_domains WHERE id={}".format(
			row[2]))
		context_domains = context_domainsBluep.copy()
		conversations['context_domains'] = getField(cur, context_domains)
		cur.execute("select * from zadanie1.context_entities WHERE id={}".format(
			row[3]))
		context_entities = context_entitiesBluep.copy()
		conversations['context_entities'] = getField(cur, context_entities)
	cur.execute("select hashtag_id from zadanie1.conversation_hashtags WHERE conversation_id={}".format(
		conversations['id']))
	hashtagId = cur.fetchall()
	for id in hashtagId:
		cur.execute("select * from zadanie1.hashtags WHERE id={}".format(
			id[0]))
		hashtags = hashtagsBluep.copy()
		conversations['hashtags'] = getField(cur, hashtags)
		break

	with open('importFile6.txt', 'a', encoding="utf-8") as data:
		data.write('{"index":{}}' + '\n')
		json.dump(conversations, data, ensure_ascii=False)
		data.write('\n')

	print(offset)
	offset += 1
	if offset >= 5000:
		break