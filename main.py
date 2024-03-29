import json
import sys
import time
from urllib.parse import parse_qsl

import oauth2 as oauth
import pandas as pd

# Your consumer key and consumer secret generated by discogs when an application is created
# and registered . See http://www.discogs.com/settings/developers . These credentials
# are assigned by application and remain static for the lifetime of your discogs application.
consumer_key = 'JJCOegYnRLCLRejtcZbo'
consumer_secret = 'UFlGrCViqSkoBNfRTGZyUfmpTGNbFbMM'

# The following oauth end-points are defined by discogs.com staff. These static endpoints
# are called at various stages of oauth handshaking.
request_token_url = 'https://api.discogs.com/oauth/request_token'
authorize_url = 'https://www.discogs.com/oauth/authorize'
access_token_url = 'https://api.discogs.com/oauth/access_token'

# A user-agent is required with Discogs API requests. Be sure to make your user-agent
# unique, or you may get a bad response.
user_agent = 'discogs_api_example/1.0'

# create oauth Consumer and Client objects using
consumer = oauth.Consumer(consumer_key, consumer_secret)
client = oauth.Client(consumer)

# pass in your consumer key and secret to the token request URL. Discogs returns
# an ouath_request_token as well as an oauth request_token secret.
resp, content = client.request(request_token_url, 'POST', headers={'User-Agent': user_agent})

# we terminate if the discogs api does not return an HTTP 200 OK. Something is
# wrong.
# TODO: Handle this error
if resp['status'] != '200':
    sys.exit('Invalid response {0}.'.format(resp['status']))

request_token = dict(parse_qsl(content.decode('utf-8')))

print(f'Please browse to the following URL {authorize_url}?oauth_token={request_token["oauth_token"]}')

# Waiting for user input
accepted = 'n'
while accepted.lower() == 'n':
    print()
    accepted = input(f'Have you authorized me at {authorize_url}?oauth_token={request_token["oauth_token"]} [y/n] :')

# request the verification token from the user.
oauth_verifier = input('Verification code : ')

# Generate objects that pass the verification key with the oauth token and oauth
# secret to the discogs access_token_url
token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
token.set_verifier(oauth_verifier)
client = oauth.Client(consumer, token)

resp, content = client.request(access_token_url, 'POST', headers={'User-Agent': user_agent})

# if verification is successful, the discogs oauth API will return an access token
# and access token secret.
access_token = dict(parse_qsl(content.decode('utf-8')))

# Now able to fetch an image using the application consumer key and secret,
# along with the verified oauth token and oauth token for this user.
token = oauth.Token(key=access_token['oauth_token'],
                    secret=access_token['oauth_token_secret'])
client = oauth.Client(consumer, token)

if resp['status'] != '200':
    sys.exit('Invalid API response {0}.'.format(resp['status']))

# Get data from discogs export
discogs = pd.read_csv('example/discogs.csv', encoding='utf8')
discogs = discogs[discogs['status'] == 'For Sale']
discogs = discogs[discogs['sleeve_condition'] == 'Mint (M)']
discogs = discogs[discogs['media_condition'] == 'Mint (M)']
# Get data from woocommerce export
wc = pd.read_csv('example/woocommerce.csv', encoding='utf8')
wc = wc[wc['Stock'] > 0]

# Drop unavailable woocommerce items from dataframe and remove added columns (caused from merge)
same = pd.merge(wc, discogs, on='Attribute 1 value(s)')
same.drop(['listing_id', 'artist', 'label', 'catno', 'format',
           'release_id', 'status', 'price', 'listed', 'comments',
           'media_condition', 'sleeve_condition', 'accept_offer', 'external_id',
           'weight', 'format_quantity', 'location', 'quantity'], axis=1, inplace=True)

same.to_csv('out_old.csv', index=False, encoding='utf8')

# Drop duplicates from new entries

for i in wc['Attribute 1 value(s)']:
    for j in discogs['Attribute 1 value(s)']:
        if i == j:
            discogs.drop(discogs.loc[discogs['Attribute 1 value(s)'] == i].index, inplace=True)
image_list = []

for i in discogs['release_id']:
    resp, content = client.request('https://api.discogs.com/releases/' + str(int(i)),
                                   headers={'User-Agent': user_agent})

    if resp['status'] != '200':
        print('unable to fetch')
        print(int(i))
        image_list.append('NaN')
    else:
        if i == 3443043:
            # TODO: This is a release without image.
            # TODO: Try - catch this error
            image_list.append('NaN')
            time.sleep(1)

        else:
            # sys.exit('Unable to fetch release')
            # load the JSON response content into a dictionary.
            print(int(i))
            release = json.loads(content.decode('utf-8'))
            # extract the first image uri.
            image = release['images'][0]['uri']
            image_list.append(image)
            time.sleep(1)  # Delay for API honor code

discogs['cover'] = image_list

# TODO: Format this dataframe for woocommerce straight compatibility
discogs.to_csv('out_new.csv', index=False, encoding='utf8')
