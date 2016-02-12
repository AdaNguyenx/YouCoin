#!/usr/bin/python
from datetime import datetime, timedelta
import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

#Coinbase
from coinbase.wallet.client import Client
import json

#replace everything in < > brackets below
##################################################
##################################################
##################################################
#coinbase information
API_KEY = <API_KEY>
API_SECRET = <API_SECRET>
Wallet_1_address = <WALLET1_ADDRESS>
Wallet_2_address = <WALLET2_ADDRESS>

#youtube information
CLIENT_SECRETS_FILE = <CLIENT_SECRETS_FILE>

#place the date your youtube account started, or the date from which
#you want to count the views to your channel
#place string in YYYY-MM-DD format. Example: "2015-01-22"
DATEYOUTUBEACCOUNTSTARTED = <DATEYOUTUBEACCOUNTSTARTED>

#place the current date, or the date from which you
#want the count of your youtube views to stop
#place string in YYYY-MM-DD format. Example: "2015-01-22"
PRESENTDATE = <PRESENTDATE>

#script information
#this variable will determine how many bitcoins you want
#to donate with each view
DONATERATE = <DONATERATE>

##################################################
##################################################
##################################################

YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
  "https://www.googleapis.com/auth/yt-analytics.readonly"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_ANALYTICS_API_SERVICE_NAME = "youtubeAnalytics"
YOUTUBE_ANALYTICS_API_VERSION = "v1"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0
To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}
For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    ))

#coinbase yo
def makeCashRain(viewChange):
  viewChange = viewChange * DONATERATE
  viewChange = str(viewChange)

  client = Client(API_KEY, API_SECRET)  

  #  Get your primary coinbase account
  primary_account = client.get_primary_account()

  # Send money
  primary_account.send_money(to=Wallet_2_address,
                     amount=viewChange,
                     currency="BTC")
  

def get_authenticated_services(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=" ".join(YOUTUBE_SCOPES),
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  http = credentials.authorize(httplib2.Http())

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=http)
  youtube_analytics = build(YOUTUBE_ANALYTICS_API_SERVICE_NAME,
    YOUTUBE_ANALYTICS_API_VERSION, http=http)

  return (youtube, youtube_analytics)





def get_channel_id(youtube):
  channels_list_response = youtube.channels().list(
    mine=True,
    part="id"
  ).execute()

  return channels_list_response["items"][0]["id"]

def run_analytics_report(youtube_analytics, channel_id, options):
  # Call the Analytics API to retrieve a report. For a list of available
  # reports, see:
  # https://developers.google.com/youtube/analytics/v1/channel_reports
  analytics_query_response = youtube_analytics.reports().query(
    ids="channel==%s" % channel_id,
    metrics=options.metrics,
    start_date=options.start_date,
    end_date=options.end_date,
  ).execute()

  # print "Analytics Data for Channel %s" % channel_id
  # print analytics_query_response

  # for column_header in analytics_query_response.get("columnHeaders", []):
  #   print "%-20s" % column_header["name"],
  # print
  record1 = open("record.txt")
  record1.seek(0)
  past = record1.read()

  past = int(past)


  record1.seek(0)
  record1.close()

  
  for row in analytics_query_response.get("rows", []):
    for value in row:
      print(value)
      if (int(value) > past):
        record2 = open("record.txt",'w')
        value = int(value)
        print value
        #newValue will equal the new amount of added views
        newValue = value - past
        makeCashRain(newValue)
        record2.write(str(value))
        record2.close()
    

  

if __name__ == "__main__":
  # now = datetime.now()
  # one_day_ago = (now - timedelta(days=1)).strftime("%Y-%m-%d")
  # one_week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")

  argparser.add_argument("--metrics", help="Report metrics",
    default="views")
  
  argparser.add_argument("--start-date", default=DATEYOUTUBEACCOUNTSTARTED,
    help="Start date, in YYYY-MM-DD format")
  argparser.add_argument("--end-date", default=PRESENTDATE,
    help="End date, in YYYY-MM-DD format")
  args = argparser.parse_args()

  (youtube, youtube_analytics) = get_authenticated_services(args)
  try:
    channel_id = get_channel_id(youtube)
    run_analytics_report(youtube_analytics, channel_id, args)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
