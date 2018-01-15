from __future__ import print_function
import discord
import httplib2
import os
import jellyfish
from cogs.utils import checks
from discord.ext import commands
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from enum import Enum
from __main__ import send_cmd_help
from configparser import SafeConfigParser
from texttable import Texttable

#   VARIABLES
CONFIG_FILE_PATH = 'data/MapleRoyals/config.ini'

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'data/MapleRoyals/client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

#   Price check source: https://docs.google.com/spreadsheets/d/1VHSCcav4Y9SDAExBYPnJbV5S8auAdChb9ylwhi_LAyQ/edit#gid=9692681
spreadsheetSource = None
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
AP_Resets_Range = None

class MapleRoyals:
    """Bot for MapleRoyals!"""
    global spreadsheetSource
    global spreadsheetID

    def __init__(self, bot):
        self.bot = bot
        InitializeConfig()
        InitializeGoogleSheetsService()

    #   Changes the status of the bot given a status message
    @commands.command(name="setstatus", aliases=["SetStatus"])
    @checks.is_owner()
    async def SetStatus(self, status):
        """Sets the status of the bot"""
        #   change status
        await self.bot.change_presence(game=discord.Game(name=status))

    @commands.group(pass_context=True, name="pc", aliases=["PriceCheck", "PC", "price", "pricecheck"])
    async def PriceCheck(self, ctx):
        """Price Check by using the commands listed below
            
            NOTE: If you do not see your price checks below, that means I (DootTheSnoot) have not coded it yet.
        """

        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        if ctx.invoked_subcommand is None:
            #await self.bot.say(ctx.message.author.mention)
            await send_cmd_help(ctx)

    #   COMMAND: CHECK UPDATE DATE
    @PriceCheck.command(name="updated", aliases=["Updated", "UpdatedDate", "updateddate","ud"], pass_context=True)
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
    @PriceCheck.command(name="weapons", aliases=["w", "W", "Weapons", "Weapon", "weapon"], pass_context=True)
    async def SayWeaponsPrices(self, ctx):
        """Show all prices for weapons.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable(weapons)
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check all scrolls
    @PriceCheck.command(name="scrolls", aliases=["Scrolls", "scroll", "Scroll", "s", "S", "armor", "Armor", "armour", "Armour"], pass_context=True)
    async def SayScrollPrices(self, ctx):
        """Show all prices for all scrolls.
        """

        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()

        #   Since there are too many scrolls for a single message, a custom table code is needed. First part of scrolls
        table = Texttable()
        table.header(["Scroll(s)","10%","30%","60%","70%","100%"])
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["l", "c", "c", "c", "c", "c"])
        table.set_cols_valign(["m", "m", "m", "m", "m", "m"])
    
        for i in range(0, 14):
            table.add_row([scrolls[i][0], scrolls[i][1], scrolls[i][2], scrolls[i][3], scrolls[i][4], scrolls[i][5]])
        
        msg = ctx.message.author.mention + "\n"  
        msg += "```md" + "\n"
        msg += table.draw()
        msg += "\n```"
        await self.bot.say(msg)

        #   Rest of scrolls
        table = Texttable()
        table.header(["Scroll(s)","10%","30%","60%","70%","100%"])
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["l", "c", "c", "c", "c", "c"])
        table.set_cols_valign(["m", "m", "m", "m", "m", "m"])
    
        for i in range(14, 27):
            table.add_row([scrolls[i][0], scrolls[i][1], scrolls[i][2], scrolls[i][3], scrolls[i][4], scrolls[i][5]])
        msg = "```md" + "\n"
        msg += table.draw()
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()
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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[0], weapons[1]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[2]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[3]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[4]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[5]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()
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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[6]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()
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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[7]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()
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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[8]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()
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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[9]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()
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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[10]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()
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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[11]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()
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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[12]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()
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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[13]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()
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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[14]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()
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
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[15]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()
        await self.bot.say(msg)

    #   Price Check all Gun
    @PriceCheck.command(name="gun", aliases=["Gun", "guns", "Guns"], pass_context=True)
    async def SayGunPrices(self, ctx):
        """Show all prices for Guns.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        weapons = GetWeaponsPrices()

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += GetFormattedWeaponsTable([weapons[16]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()
        await self.bot.say(msg)

    #   Price Check all helmets
    @PriceCheck.command(name="helmet", aliases=["Helmet", "hel", "Hel", "h" "H","helm", "Helm"], pass_context=True)
    async def SayHelmetPrices(self, ctx):
        """Show all prices for Helmets.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += GetFormattedScrollsTable([scrolls[0],scrolls[1],scrolls[2]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check all Overalls
    @PriceCheck.command(name="overall", aliases=["Overall", "overalls", "Overalls", "oa" "OA"], pass_context=True)
    async def SayOverallPrices(self, ctx):
        """Show all prices for Overalls.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += GetFormattedScrollsTable([scrolls[3],scrolls[4],scrolls[5],scrolls[6]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check all shoes
    @PriceCheck.command(name="shoes", aliases=["Shoes", "shoe", "Shoe"], pass_context=True)
    async def SayShoePrices(self, ctx):
        """Show all prices for Shoes.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += GetFormattedScrollsTable([scrolls[7],scrolls[8]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check all capes
    @PriceCheck.command(name="capes", aliases=["Capes", "cape", "Cape"], pass_context=True)
    async def SayCapePrices(self, ctx):
        """Show all prices for capes.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += GetFormattedScrollsTable([scrolls[9],scrolls[10], scrolls[11], scrolls[12]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check all Face
    @PriceCheck.command(name="face", aliases=["Face", "faces", "Faces"], pass_context=True)
    async def SayFacePrices(self, ctx):
        """Show all prices for faces.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += GetFormattedScrollsTable([scrolls[13]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check all topwear
    @PriceCheck.command(name="topwear", aliases=["Topwear", "topwears", "Topwears", "top", "Top"], pass_context=True)
    async def SayTopwearPrices(self, ctx):
        """Show all prices for topwears.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += GetFormattedScrollsTable([scrolls[14], scrolls[15]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check all bottomwear
    @PriceCheck.command(name="bottomwear", aliases=["Bottomwear", "bottomwears", "Bottomwears", "bottom", "Bottom"], pass_context=True)
    async def SayBottomwearPrices(self, ctx):
        """Show all prices for bottomwears.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += GetFormattedScrollsTable([scrolls[16], scrolls[17]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check all gloves
    @PriceCheck.command(name="glove", aliases=["Glove", "Gloves", "gloves"], pass_context=True)
    async def SayGlovePrices(self, ctx):
        """Show all prices for gloves.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += GetFormattedScrollsTable([scrolls[18], scrolls[19]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check all shields
    @PriceCheck.command(name="shield", aliases=["Shield", "shields", "Shields"], pass_context=True)
    async def SayShieldPrices(self, ctx):
        """Show all prices for shields.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += GetFormattedScrollsTable([scrolls[20], scrolls[21]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check all Eye
    @PriceCheck.command(name="eye", aliases=["Eye", "eyes", "Eyes"], pass_context=True)
    async def SayEyePrices(self, ctx):
        """Show all prices for eyes.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += GetFormattedScrollsTable([scrolls[22], scrolls[23]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check all earring
    @PriceCheck.command(name="earring", aliases=["Earring", "earrings", "Earrings"], pass_context=True)
    async def SayEarringPrices(self, ctx):
        """Show all prices for earring.
        """
        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        scrolls = GetScrollPrices()

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += GetFormattedScrollsTable([scrolls[24], scrolls[25], scrolls[26]])
        msg += "\n```"
        msg += "\nSource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check heartstoppers
    @PriceCheck.command(name="heartstopper", aliases=["Heartstopper", "hs", "HS"], pass_context=True)
    async def SayHeartstopperPrices(self, ctx):
        """Show all prices for heartstoppers.
        """

        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        #   Get hearstopper range
        result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=HeartstopperRange).execute()
        hearstopperRange = result.get('values', [])

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += hearstopperRange[0][0]
        msg += "\n```"
        msg += "\nsource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check Onyx apples
    @PriceCheck.command(name="onyxapple", aliases=["OnyxApple", "onyxapples", "OnyxApples", "onyx", "Onyx", "Apple", "apple"], pass_context=True)
    async def SayOnyxApplePrices(self, ctx):
        """Show all prices for Onyx Apples.
        """

        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        #   Get hearstopper range
        result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=OnyxAppleRange).execute()
        miscRange = result.get('values', [])

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += miscRange[0][0]
        msg += "\n```"
        msg += "\nsource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check white scrolls
    @PriceCheck.command(name="ws", aliases=["WhiteScroll", "WhiteScrolls", "whitescrolls", "whitescroll", "WS", "white", "White"], pass_context=True)
    async def SayWSPrices(self, ctx):
        """Show all prices for White Scrolls.
        """

        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        #   Get hearstopper range
        result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=WhiteScrollRange).execute()
        miscRange = result.get('values', [])

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += miscRange[0][0]
        msg += "\n```"
        msg += "\nsource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check chaos scrolls
    @PriceCheck.command(name="cs", aliases=["ChaosScroll", "chaosscroll", "chaosscrolls", "ChaosScrolls", "CS", "chaos", "Chaos"], pass_context=True)
    async def SayCSPrices(self, ctx):
        """Show all prices for Chaos Scrolls.
        """

        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        #   Get hearstopper range
        result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=ChaosScrollRange).execute()
        miscRange = result.get('values', [])

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += miscRange[0][0]
        msg += "\n```"
        msg += "\nsource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

    #   Price Check AP Resets
    @PriceCheck.command(name="ap", aliases=["AP", "APR", "apr", "apreset", "APReset", "apresets", "APResets"], pass_context=True)
    async def SayCSPrices(self, ctx):
        """Show all prices for AP Resets.
        """

        #   Add "typing... " status
        await self.bot.send_typing(ctx.message.channel)

        #   Get hearstopper range
        result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=AP_Resets_Range).execute()
        miscRange = result.get('values', [])

        msg = ctx.message.author.mention + "\n"
        msg += "```md" + "\n"
        msg += miscRange[0][0]
        msg += "\n```"
        msg += "\nsource: " + spreadsheetSource
        msg += "\n"+ GetPriceUpdateDate()

        await self.bot.say(msg)

def setup(bot):
    bot.add_cog(MapleRoyals(bot))
    
#   Returns the SheetsService from the Google sheets API
def InitializeGoogleSheetsService():
    #   Create references to globals
    global SheetsService
    #   Initialize Google API credentials
    print ("Initializing Google sheets services...")
    SheetsService = discovery.build('sheets', 'v4',  developerKey='AIzaSyD81_C0xYmRHR5bHqZxwtWVhJe4vQQXw9Y')

#   Parse the config file and evaluate
def InitializeConfig():
    print("Initializing config...")

    config = SafeConfigParser()
    config.read(CONFIG_FILE_PATH)

    #   Create references to globals
    global spreadsheetSource
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
    global AP_Resets_Range

    #   Assign variables from config
    #   Main Settings
    spreadsheetSource = config.get("Settings", "price spreadsheet source")
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
    AP_Resets_Range = config.get('Spreadsheet Price Ranges', 'AP resets')

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

#   Returns formatted table for weapons given list of tuples
def GetFormattedWeaponsTable(weapons):
    #   Create table format
    table = Texttable()
    table.header(["Weapon(s)","10%","30%","60%","70%","100% Event"])
    table.set_deco(Texttable.HEADER)
    table.set_cols_align(["l", "c", "c", "c", "c", "c"])
    table.set_cols_valign(["m", "m", "m", "m", "m", "m"])
    for weapon in weapons:
        table.add_row([weapon[0], weapon[1], weapon[2], weapon[3], weapon[4], weapon[5]])
    return table.draw()

#   Returns formatted table for scrolls given list of tuples
def GetFormattedScrollsTable(scrolls):
    #   Create table format
    table = Texttable()
    table.header(["Scroll(s)","10%","30%","60%","70%","100%"])
    table.set_deco(Texttable.HEADER)
    table.set_cols_align(["l", "c", "c", "c", "c", "c"])
    table.set_cols_valign(["m", "m", "m", "m", "m", "m"])
    
    for scroll in scrolls:
        table.add_row([scroll[0], scroll[1], scroll[2], scroll[3], scroll[4], scroll[5]])
    return table.draw()

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
        print("")
        if i == 1:
            continue
            #   Add the 100% prices to the tuple
            #weaponsPrices[i] = weaponsPrices[i] + "-----"
        #   Skip after index of 1 because there is no 1H 100% magic price
        else:
            #   Add the 100% prices to the tuple
            weaponsPrices[i] = weaponsPrices[i] + (row[0],)

    #   Reduce name size and add empty value for 1H sword for M.Att in the 100% event slot
    weaponsPrices[0] = ("One-Hand Sword (Atk)", weaponsPrices[0][1], weaponsPrices[0][2], weaponsPrices[0][3], weaponsPrices[0][4], weaponsPrices[0][5])
    weaponsPrices[1] = ("One-Hand Sword (M.Atk)", weaponsPrices[1][1], weaponsPrices[1][2], weaponsPrices[1][3], weaponsPrices[1][4], "-----")
    
    print("\n")
    for weapon in weaponsPrices:
        print(weapon)

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

    scrolls = []

    #   Get 10%-100% helmet range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=HelmetRange).execute()
    normalValues = result.get('values', [])
    print("Fetching helmets...")
    #   append each row to tuple list
    for row in enumerate(normalValues):
        row[1][0] = "(Helmet) " + row[1][0]
        scrolls.append(tuple(row[1]))

    #   Get 10%-100% Overall range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=OverallRange).execute()
    normalValues = result.get('values', [])
    print("Fetching overalls...")
    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Overall) " + row[1][0]
        scrolls.append(tuple(row[1]))

    #   Get 10%-100% Shoes range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=ShoesRange).execute()
    normalValues = result.get('values', [])
    print("Fetching shoes...")
    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Shoes) " + row[1][0]
        scrolls.append(tuple(row[1]))

    #   Get 10%-100% Cape range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=CapeRange).execute()
    normalValues = result.get('values', [])
    print("Fetching capes...")
    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Cape) " + row[1][0]
        scrolls.append(tuple(row[1]))

    #   Get 10%-100% Face range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=FaceRange).execute()
    normalValues = result.get('values', [])
    print("Fetching face...")
    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Face) " + row[1][0]
        scrolls.append(tuple(row[1]))

    #   Get 10%-100% Topwear range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=TopwearRange).execute()
    normalValues = result.get('values', [])
    print("Fetching topwears...")
    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Topwear) " + row[1][0]
        scrolls.append(tuple(row[1]))

        #   Get 10%-100% Bottomwear range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=BottomwearRange).execute()
    normalValues = result.get('values', [])
    print("Fetching bottomwear...")
    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Bottomwear) " + row[1][0]
        scrolls.append(tuple(row[1]))

        #   Get 10%-100% Gloves range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=GlovesRange).execute()
    normalValues = result.get('values', [])
    print("Fetching gloves...")
    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Gloves) " + row[1][0]
        scrolls.append(tuple(row[1]))

        #   Get 10%-100% Shield range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=ShieldRange).execute()
    normalValues = result.get('values', [])
    print("Fetching shield...")
    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Shield) " + row[1][0]
        scrolls.append(tuple(row[1]))

        #   Get 10%-100% Eye range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=EyeRange).execute()
    normalValues = result.get('values', [])
    print("Fetching eye...")
    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Eye) " + row[1][0]
        scrolls.append(tuple(row[1]))

        #   Get 10%-100% Earring range
    result = SheetsService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=EarringRange).execute()
    normalValues = result.get('values', [])
    print("Fetching earrings...")
    #   append each row to tuple list
    for row in enumerate(normalValues):   
        row[1][0] = "(Earring) " + row[1][0]
        scrolls.append(tuple(row[1]))
    
    #print("\n")
    #for scroll in scrollPrices:
    #    print(scroll)
    return scrolls
