import os.path
import sys

import requests
try:
	import apiai
except ImportError:
	sys.path.append(
		os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

		)
	import apiai
import urllib, json
from yelp.client import Client as YelpClient 
from yelp.oauth1_authenticator import Oauth1Authenticator
import uuid

session = uuid.uuid4().hex

CLIENT_ACCESS_TOKEN = '0b34236675c04a559bcefc637d60d285'

GOOGLE_API_KEY = 'AIzaSyAEaFFa4epR8p58idnt4Dg-xm8gVBHNE18'

YELP_CONSUMER_KEY = 'FuALLjOGK-d4ky3cRmSsuA'
YELP_CONSUMER_SECRET = 'PyJxdT2NnQ1IXT4fmIo5vRkMT_4'
YELP_TOKEN = 'rYylw7xYVq8sgMgQa4TfZY0GwqbhN2B1'
YELP_TOKEN_SECRET = 'WFCI5m5uiOrAOmgAn4Kji_QDNOQ'


def build_URL(search_text='', type_text=''):
	base_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json' 
	key_string = '?key='+GOOGLE_API_KEY
	query_string = '&query='+urllib.parse.quote(search_text)
	sensor_string = '&sensor=false'
	type_string = ''
		
	if type_text!= '':
		type_string = '&types='+urllib.quote(types_text)
	url = base_url+key_string+query_string+sensor_string+type_string
	return url

def google_place_search( text, typ='' ):
	print('\n')
	print('Google:')
	res = requests.get( build_URL( text,typ) )
	rr = res.json().get('results')

	if not rr:
		print("nothing from Google!")
		return None
	google_list = []	
	for r in rr:
		
		print(r.get('name'))
		
		google_list.append(r.get('name'))	
	print('\n')
	
	return google_list


def main():
	
	ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, session_id = session)
	request = ai.text_request()
	request.language = 'en'

	inp = input('Describe what kind of a place you would like to go to!')

	request.query = inp

	response_api = request.getresponse()

	rstr = response_api.read().decode('utf-8')
	json_obj = json.loads(rstr) 
	result = json_obj.get('result')
	incomplete = result.get('actionIncomplete')
	speech = result.get('fulfillment').get('speech')
	
	
	if result.get('actionIncomplete') == False:

		params = result.get('parameters')
		rtype = params.get('type')
		rcity= params.get('geo-city')
		rplace = params.get('place')
		rrank = params.get('rank')



	else:
		while result.get('actionIncomplete') == True:
			if result.get('actionIncomplete') == True:	
				ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, session_id = session)
				new_request = ai.text_request()
				new_request.language = 'en'

				new_inp = input(speech)

				new_request.query = new_inp

				new_response_api = new_request.getresponse()

				new_rstr = new_response_api.read().decode('utf-8')
				new_json_obj = json.loads(new_rstr) 
				result = new_json_obj.get('result')
				speech = result.get('fulfillment').get('speech')
				params = result.get('parameters')
				rtype = params.get('type')
				rcity= params.get('geo-city')
				rplace = params.get('place')
				rrank = params.get('rank')


	rparams= [rtype, rcity, rplace, rrank]
	rrparams = rtype + '+'+ rplace + '+' + rcity 	
	if rrank != '':
		rrparams = rtype + '+'+ rplace + '+' + rcity + '+' + rrank
	srch = rrparams
	
	google_list=google_place_search( srch )
	
	auth = Oauth1Authenticator(
		consumer_key=YELP_CONSUMER_KEY,
		consumer_secret=YELP_CONSUMER_SECRET,
		token=YELP_TOKEN,
		token_secret=YELP_TOKEN_SECRET
		)
	client_yelp = YelpClient(auth)
	yelp_params = {
	'term': rtype, 
	'category': rplace,
	'lang': 'en'
	}
	
	matches = []
	for obj in client_yelp.search(rcity, rrank,**yelp_params).businesses:
			matches.append(obj.name)
	
	 
	print('Yelp: ')
	for m in matches:
		
		print(m)		
	
	google_list = [item.lower() for item in google_list]
	matches = [match.lower() for match in matches]
	same = []
	for place in google_list:
		if place in matches:
			same.append(place)
	
	same = [sa.title() for sa in same]
	print('\n')
	print('Same: ')
	for q in same:
		print(q)

	print('\n')
	print ('Different: ')	
	different = []
	for place in google_list:
		if place not in matches:
			different.append(place)
	for place in matches:
		if place not in google_list:
			different.append(place)
	different = [elm.title() for elm in different]		
	for el in different:		
		print(el)		
	
if __name__ == '__main__':
	main()				
