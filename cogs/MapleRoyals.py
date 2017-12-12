from __future__ import print_function
import discord
import httplib2
import os
import jellyfish
from discord.ext import commands
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from enum import Enum
from configparser import SafeConfigParser

#   VARIABLES
CONFIG_FILE_PATH = 'data/MapleRoyals/config.ini'

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'data/MapleRoyals/client_secret.json'
#APPLICATION_NAME = 'Google Sheets API Python Quickstart'

#   Price check source: https://docs.google.com/spreadsheets/d/1VHSCcav4Y9SDAExBYPnJbV5S8auAdChb9ylwhi_LAyQ/htmlview#
spreadsheetID = None
#   Spreadsheet ranges of each category
UpdatedDateRange = None
WeaponsNormalRange = None
WeaponsEventRange = None
HelmetRange = None
OverallRange = None
ShoesRange = None
CapeRange = None
FaceRange = None
TopwearRange = None
BottomwearRange = None
GlovesRange = None
ShieldRange = None
EyeRange = None
EarringRange = None
HeartstopperRange = None
OnyxAppleRange = None
WhiteScrollRange = None
ChaosScrollRange = None

class MapleRoyals:
    """Bot for MapleRoyals!"""

    def __init__(self, bot):
        self.bot = bot
        InitializeConfig()

    #   COMMAND: PRICE CHECK
    @commands.command(pass_context=True)
    async def pc(self, ctx, category: str):
        """Used for Price Checking.

           write more stuff here...
        """
        
        #   Evaluate catagory
        if jellyfish.jaro_distance(category.lower(), 'weapons') > .80:
            weapons = GetWeaponsPC()
            #for weapon in weapons:
            #print(weapons)

        msg = GetPriceUpdateDate()

        #await self.bot.say(msg)

def setup(bot):
    bot.add_cog(MapleRoyals(bot))

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

#   Parse the config file and evaluate
def InitializeConfig():
    print("Initializing config...")

    config = SafeConfigParser()
    config.read(CONFIG_FILE_PATH)

    #   Assign variables from config
    #   Main Settings
    spreadsheetID = config.get('Settings', 'price spreadsheet ID')
    #   Scrolls section
    UpdatedDateRange = config.get('Spreadsheet Price Ranges', 'price updated date')
    WeaponsNormalRange = config.get('Spreadsheet Price Ranges', 'weapons 10%/30%/60%/70%')
    WeaponsEventRange = config.get('Spreadsheet Price Ranges', 'weapons 100% event')
    HelmetRange = config.get('Spreadsheet Price Ranges', 'helmet')
    OverallRange = config.get('Spreadsheet Price Ranges', 'overall')
    ShoesRange = config.get('Spreadsheet Price Ranges', 'shoes')
    CapeRange = config.get('Spreadsheet Price Ranges', 'cape')
    FaceRange = config.get('Spreadsheet Price Ranges', 'face')
    TopwearRange = config.get('Spreadsheet Price Ranges', 'topwear')
    BottomwearRange = config.get('Spreadsheet Price Ranges', 'bottomwear')
    GlovesRange = config.get('Spreadsheet Price Ranges', 'gloves')
    ShieldRange = config.get('Spreadsheet Price Ranges', 'shield')
    EyeRange = config.get('Spreadsheet Price Ranges', 'eye')
    EarringRange = config.get('Spreadsheet Price Ranges', 'earring')
    HeartstopperRange = config.get('Spreadsheet Price Ranges', 'heartstopper')
    OnyxAppleRange = config.get('Spreadsheet Price Ranges', 'onyx apple')
    WhiteScrollRange = config.get('Spreadsheet Price Ranges', 'white scroll')
    ChaosScrollRange = config.get('Spreadsheet Price Ranges', 'chaos scroll')

#   Returns date of updates
def GetPriceUpdateDate():
    service = GetSheetsService()
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=UpdatedDateRange).execute()
    values = result.get('values', [])

    if not values:
        return 'No data found.'
    else:
        return values[0][0]

#   Returns tuple of weapons 
def GetWeaponsPC():
    weaponsPrices = []

    #   Get 10%-70% weapon range
    print("Weapons range: " + str(WeaponsNormalRange))
    service = GetSheetsService()
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=WeaponsNormalRange).execute()
    normalValues = result.get('values', [])

    #   append each row
    for row in enumerate(normalValues):   
        #   Convert list to tuple
        weaponsPrices.append(tuple(row[1]))

    #   Get 100% event weapon range
    service = GetSheetsService()
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=WeaponsEventRange).execute()
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