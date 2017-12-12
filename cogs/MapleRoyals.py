from __future__ import print_function
import discord
import httplib2
import os
from discord.ext import commands
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from enum import Enum

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

#   VARIABLES

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'data/MapleRoyals/client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

#   Price check source: https://docs.google.com/spreadsheets/d/1VHSCcav4Y9SDAExBYPnJbV5S8auAdChb9ylwhi_LAyQ/htmlview#
spreadsheetId = '1VHSCcav4Y9SDAExBYPnJbV5S8auAdChb9ylwhi_LAyQ'

class Catagory(Enum):
    WEAPONS = 1
    HELMET = 2
    OVERALL = 3
    SHOES = 4
    CAPE = 5
    FACE = 6
    TOPWEAR = 7
    BOTTOMWEAR = 8
    GLOVES = 9
    SHIELD = 10
    EYE = 11
    EARRING = 12
    HEARTSTOPPERS = 13
    ONYX_APPLE = 14
    WHITE_SCROLL = 15
    WS = 16
    CHAOS_SCROLL = 17
    CS = 18

class Mycog:
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot

    #   COMMAND: PRICE CHECK
    @commands.command(pass_context=True)
    async def pc(self, ctx, category: str):
        """Used for Price Checking.

           write more stuff here...
        """
        
        #   Evaluate catagory
        if category.upper() == Catagory.WEAPONS.name:
            weapons = GetWeaponsPC()
            #for weapon in weapons:
            #print(weapons)

        msg = GetUpdatedDate()

        #await self.bot.say(msg)

def setup(bot):
    bot.add_cog(Mycog(bot))

#   Returns the service from the Google sheets API
def GetSheetsService():
    #   Initialize Google API credentials
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?''version=v4')
    return discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

#   Returns credentials for Google API
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

#   Returns date of updates
def GetUpdatedDate():
    rangeName = 'Scrolls!A1:H'
    service = GetSheetsService()
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        return 'No data found.'
    else:
        return values[0][0]

#   Returns tuple of weapons 
def GetWeaponsPC():
    weaponsPrices = []

    #   Get 10%-70% weapon range
    rangeName = 'Scrolls!A7:E23'
    service = GetSheetsService()
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
    normalValues = result.get('values', [])

    #   append each row
    for row in enumerate(normalValues):   
        #   Convert list to tuple
        weaponsPrices.append(tuple(row[1]))

    #   Get 100% event weapon range
    rangeName = 'Scrolls!S4:S19'
    service = GetSheetsService()
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
    eventValues = result.get('values', [])

    #   Loop through each weapon and add
    for i, row in enumerate(eventValues):
        if i == 0:
            #   Add the 100% prices to the tuple
            weaponsPrices[i] = weaponsPrices[i] + (row[0],)
        #   Skip after index of 1 because there is no 1H 100% magic price
        else:
            #   Add the 100% prices to the tuple
            weaponsPrices[i+1] = weaponsPrices[i+1] + (row[0],)

    #   Add headers
    weaponsPrices.insert(0, ("Weapons","10%","30%","60%","70%","100% Event",)) 

    #print("\n")
    #for weapon in weaponsPrices:
    #    print(weapon)

    return weaponsPrices