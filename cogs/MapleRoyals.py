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
from __main__ import send_cmd_help
from configparser import SafeConfigParser

#   VARIABLES
CONFIG_FILE_PATH = 'data/MapleRoyals/config.ini'

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'data/MapleRoyals/client_secret.json'
#APPLICATION_NAME = 'Google Sheets API Python Quickstart'

#   Price check source: https://docs.google.com/spreadsheets/d/1VHSCcav4Y9SDAExBYPnJbV5S8auAdChb9ylwhi_LAyQ/edit#gid=9692681
spreadsheetID = None
SheetsService = None
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
        InitializeGoogleSheetsService()

    @commands.group(pass_context=True, name="PriceCheck", aliases=["pc", "PC", "price", "pricecheck"])
    async def PriceCheck(self, ctx):
        """Price Check"""

        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        if ctx.invoked_subcommand is None:
            #await self.bot.say(ctx.message.author.mention)
            await send_cmd_help(ctx)

    #   COMMAND: CHECK UPDATE DATE
    @PriceCheck.command(name="UpdatedDate", aliases=["updated", "updateddate","ud"], pass_context=True)
    async def SayUpdatedDate(self, ctx):
        """
            Display last updated date.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        msg = ctx.message.author.mention + "\n"
        msg += GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check all weapons
    @PriceCheck.command(name="weapons", aliases=["w", "W", "Weapons", "Weapon", "weapon"], pass_context=False)
    async def SayWeaponsPrices(self, ctx):
        """Show all prices for weapons.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()
        #   Add headers
        weapons.insert(0, ("Weapon(s)","10%","30%","60%","70%","100% Event",)) 

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons)

        await self.bot.say(msg)

    #   Price Check all scrolls
    @PriceCheck.command(name="scrolls", aliases=["Scrolls", "scroll", "Scroll", "s", "S"], pass_context=False)
    async def SayScrollPrices(self, ctx):
        """Show all prices for all scrolls.
        """

        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()
        #   Add headers
        scrolls.insert(0, ("Scroll(s)","10%","30%","60%","70%","100%",)) 

        msg = ctx.message.author.mention + "\n"  
        msg += str(scrolls)

        await self.bot.say(msg)

    #   Price Check all 1-handed swords
    @PriceCheck.command(name="1hs", aliases=["1HSword", "1HS", "1-HS", "1-hs" "OneHandedSword", "1HandedSword" "One-HandedSword", "1-HandedSword"], pass_context=True)
    async def SayOneHandedSwordPrices(self, ctx):
        """Show all prices for 1H Sword (Attack & Magic).
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[0])
        msg += str(weapons[1])
        await self.bot.say(msg)

    #   Price Check all 2-handed swords
    @PriceCheck.command(name="2hs", aliases=["2HSword", "2HS", "2-HS", "2-hs" "TwoHandedSword", "2HandedSword" "Two-HandedSword", "2-HandedSword"], pass_context=True)
    async def SayTwoHandedSwordPrices(self, ctx):
        """Show all prices for 2H Sword.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[2])
        await self.bot.say(msg)

    #   Price Check all 1-handed axes
    @PriceCheck.command(name="1ha", aliases=["1HAxe", "1HA", "1-HA", "1-ha" "OneHandedAxe", "1HandedAxe" "One-HandedAxe", "1-HandedAxe"], pass_context=True)
    async def SayOneHandedAxePrices(self, ctx):
        """Show all prices for 1H Axe.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[3])
        await self.bot.say(msg)

    #   Price Check all 2-handed Axe
    @PriceCheck.command(name="2ha", aliases=["2HAxe", "2HA", "2-HA", "2-ha" "TwoHandedAxe", "2HandedAxe" "Two-HandedAxe", "2-HandedAxe"], pass_context=True)
    async def SayTwoHandedAxePrices(self, ctx):
        """Show all prices for 2H Axe.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[4])
        await self.bot.say(msg)

    #   Price Check all 1-handed BW
    @PriceCheck.command(name="1hbw", aliases=["1HBW", "1-BW", "1-bw" "OneHandedBluntWeapon", "1HandedBluntWeapon" "One-HandedBluntWeapon", "1-HandedBluntWeapon"], pass_context=True)
    async def SayOneHandedBluntWeaponPrices(self, ctx):
        """Show all prices for 1H Blunt Weapon.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[5])
        await self.bot.say(msg)

    #   Price Check all 2-handed BW
    @PriceCheck.command(name="2hbw", aliases=["2HBW", "2-BW", "2-bw" "TwoHandedBluntWeapon", "2HandedBluntWeapon" "Two-HandedBluntWeapon", "2-HandedBluntWeapon"], pass_context=True)
    async def SayTwoHandedBluntWeaponPrices(self, ctx):
        """Show all prices for 2H Blunt Weapon.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[6])
        await self.bot.say(msg)

    #   Price Check all Bow
    @PriceCheck.command(name="bow", aliases=["Bow", "b", "B"], pass_context=True)
    async def SayBowPrices(self, ctx):
        """Show all prices for Bow.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[7])
        await self.bot.say(msg)

    #   Price Check all Crossbow
    @PriceCheck.command(name="crossbow", aliases=["Crossbow", "xbow", "Xbow", "x-bow", "X-bow"], pass_context=True)
    async def SayCrossbowPrices(self, ctx):
        """Show all prices for Crossbow.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[8])
        await self.bot.say(msg)

    #   Price Check all Claw
    @PriceCheck.command(name="claw", aliases=["Claw"], pass_context=True)
    async def SayClawPrices(self, ctx):
        """Show all prices for Claw.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[9])
        await self.bot.say(msg)

    #   Price Check all Dagger
    @PriceCheck.command(name="dagger", aliases=["Dagger", "dag", "Dag"], pass_context=True)
    async def SayDaggerPrices(self, ctx):
        """Show all prices for Dagger.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[10])
        await self.bot.say(msg)

    #   Price Check all Spear
    @PriceCheck.command(name="spear", aliases=["Spear", "spears", "Spears"], pass_context=True)
    async def SaySpearPrices(self, ctx):
        """Show all prices for Spear.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[11])
        await self.bot.say(msg)

    #   Price Check all Polearm
    @PriceCheck.command(name="polearm", aliases=["Polearm", "pa", "PA"], pass_context=True)
    async def SayPolearmPrices(self, ctx):
        """Show all prices for Polearm.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[12])
        await self.bot.say(msg)

    #   Price Check all Wand
    @PriceCheck.command(name="wand", aliases=["Wand", "wands", "Wands"], pass_context=True)
    async def SayWandPrices(self, ctx):
        """Show all prices for Wands.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[13])
        await self.bot.say(msg)

    #   Price Check all Staff
    @PriceCheck.command(name="staff", aliases=["Staff", "staffs", "Staffs"], pass_context=True)
    async def SayStaffPrices(self, ctx):
        """Show all prices for Staffs.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[14])
        await self.bot.say(msg)

    #   Price Check all Knuckle
    @PriceCheck.command(name="knuckle", aliases=["Knuckle"], pass_context=True)
    async def SayKnucklePrices(self, ctx):
        """Show all prices for Knuckles.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[15])
        await self.bot.say(msg)

    #   Price Check all Gun
    @PriceCheck.command(name="gun", aliases=["Gun"], pass_context=True)
    async def SayGunPrices(self, ctx):
        """Show all prices for Guns.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += str(weapons[16])
        await self.bot.say(msg)

    #   Price Check all helmets
    @PriceCheck.command(name="helmet", aliases=["Helmet", "hel", "Hel", "h" "H"], pass_context=True)
    async def SayHelmetPrices(self, ctx):
        """Show all prices for Helmets.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()
        #   Add headers
        scrolls.insert(0, ("Scroll(s)","10%","30%","60%","70%","100%",))

        msg = ctx.message.author.mention + "\n"
        msg += str(scrolls[0])
        msg += str(scrolls[1])
        msg += str(scrolls[2])
        msg += str(scrolls[3])
        await self.bot.say(msg)



def setup(bot):
    bot.add_cog(MapleRoyals(bot))
    
#   Returns the SheetsService from the Google sheets API
def InitializeGoogleSheetsService():
    #   Create references to globals
    global SheetsService
    #   Initialize Google API credentials
    print ("Initializing Google sheets services...")
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?''version=v4')
    SheetsService = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

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

    #   Create references to globals
    global spreadsheetID
    global UpdatedDateRange
    global WeaponsNormalRange
    global WeaponsEventRange
    global HelmetRange
    global OverallRange
    global ShoesRange
    global CapeRange
    global FaceRange
    global TopwearRange
    global BottomwearRange
    global GlovesRange
    global ShieldRange
    global EyeRange
    global EarringRange
    global HeartstopperRange
    global OnyxAppleRange
    global WhiteScrollRange
    global ChaosScrollRange

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
    #   Create references to globals
    global SheetsService
    global spreadsheetID
    global UpdatedDateRange

    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=UpdatedDateRange).execute()
    values = result.get('values', [])

    if not values:
        return 'No data found.'
    else:
        return values[0][0]

#   Returns tuple of weapons 
def GetWeaponsPrices():
    #   Create references to globals
    global SheetsService
    global spreadsheetID
    global WeaponsNormalRange
    global WeaponsEventRange

    weaponsPrices = []

    #   Get 10%-70% weapon range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=WeaponsNormalRange).execute()
    normalValues = result.get('values', [])

    #   append each row
    for row in enumerate(normalValues):   
        #   Convert list to tuple
        weaponsPrices.append(tuple(row[1]))

    #   Get 100% event weapon range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=WeaponsEventRange).execute()
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

    #print("\n")
    #for weapon in weaponsPrices:
    #    print(weapon)

    return weaponsPrices

#   Returns tuple of all scrolls
def GetScrollPrices():
    #   Create references to globals
    global SheetsService
    global spreadsheetID
    global HelmetRange
    global OverallRange
    global ShoesRange
    global CapeRange
    global FaceRange
    global TopwearRange
    global BottomwearRange
    global GlovesRange
    global ShieldRange
    global EyeRange
    global EarringRange

    scrollPrices = []

    #   Get 10%-100% helmet range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=HelmetRange).execute()
    normalValues = result.get('values', [])

    #   append each row to tuple list
    for row in enumerate(normalValues):
        row[1][0] = "(Helmet) " + row[1][0]
        scrollPrices.append(tuple(row[1]))

    #   Get 10%-100% Overall range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=OverallRange).execute()
    normalValues = result.get('values', [])

    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Overall) " + row[1][0]
        scrollPrices.append(tuple(row[1]))

    #   Get 10%-100% Shoes range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=ShoesRange).execute()
    normalValues = result.get('values', [])

    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Shoes) " + row[1][0]
        scrollPrices.append(tuple(row[1]))

    #   Get 10%-100% Cape range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=CapeRange).execute()
    normalValues = result.get('values', [])

    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Cape) " + row[1][0]
        scrollPrices.append(tuple(row[1]))

    #   Get 10%-100% Face range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=FaceRange).execute()
    normalValues = result.get('values', [])

    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Face) " + row[1][0]
        scrollPrices.append(tuple(row[1]))

    #   Get 10%-100% Topwear range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=TopwearRange).execute()
    normalValues = result.get('values', [])

    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Topwear) " + row[1][0]
        scrollPrices.append(tuple(row[1]))

        #   Get 10%-100% Bottomwear range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=BottomwearRange).execute()
    normalValues = result.get('values', [])

    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Bottomwear) " + row[1][0]
        scrollPrices.append(tuple(row[1]))

        #   Get 10%-100% Gloves range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=GlovesRange).execute()
    normalValues = result.get('values', [])

    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Gloves) " + row[1][0]
        scrollPrices.append(tuple(row[1]))

        #   Get 10%-100% Shield range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=ShieldRange).execute()
    normalValues = result.get('values', [])

    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Shield) " + row[1][0]
        scrollPrices.append(tuple(row[1]))

        #   Get 10%-100% Eye range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=EyeRange).execute()
    normalValues = result.get('values', [])

    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Eye) " + row[1][0]
        scrollPrices.append(tuple(row[1]))

        #   Get 10%-100% Earring range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=EarringRange).execute()
    normalValues = result.get('values', [])

    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Earring) " + row[1][0]
        scrollPrices.append(tuple(row[1]))

    #print("\n")
    #for scroll in scrollPrices:
    #    print(scroll)
    return scrollPrices
