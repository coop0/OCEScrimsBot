import discord
import pickle
import pymongo
from pymongo import MongoClient
from discord.ext import commands

cluster = MongoClient()

db = cluster["discord"]
teamscollection = db["teams"]
admins = db["admins"]
client = commands.Bot(command_prefix = "!")

#command = ["!accept teamname", "!create teamname hexidecimal-colour",
  #         "!invite teamname @player", "!leave teamname",
   #        "!kick teamname @player", "!teams", "!team teamname",
    #       "!scrimpartner @teamname", "!scrim"]
command = ['!create "teamname" [Use this command to create a team]',
           "!colourchange @teamname [Changes your colour. Pro tip - Use Hexadecimal]",
           '!invite "teamname" @player [Use this command to invite a player to join a team you are in]',
           '!accept "teamname" [Use this command to accept an invite to a team]',
           "!teams [Displays a list of teams on the server]",
           '!team "teamname" [Displays the players on a team]',
           "!scrimpartner @teamname [Use this command to partner with a scrim team. Once both teams partner each other, both teams will be notified when they are looking for scrims]",
           "!scrimnow [Sends a notification in the Looking For Scrims Channel]",
           "!scrimlater [Sends a message in the Looking For Scrims Channel with your planned timeframe]"]



@client.event
async def on_ready():
    print('Bot is ready.')
@client.command()
async def accept(ctx, teamname): # unsure if working
    user = ctx.message.author
    found = False
    data = teamscollection.find({"teamname": teamname})
    for teams in data:
        if user.id in teams["invites"]:
                role = discord.utils.get(ctx.guild.roles, name=teamname)  
                await user.add_roles(role)
                await ctx.send(user.mention + " has been added to team: " + teamname)
                found = True
                a = teams["invites"]
                a.remove(user.id)
                newvalues = { "$set": { "invites": a } }
                b= teams["players"]
                b.append(user.id)
                c = teams["playersobj"]
                newb = { "$set": { "players": b} }
                newc = { "$set": { "playersobj": c } }

                teamscollection.update_one({"teamname": teamname}, newvalues)
                teamscollection.update_one({"teamname": teamname}, newc)
                teamscollection.update_one({"teamname": teamname}, newb)

                break
        else:
            await ctx.send(user.mention + " You have no pending invites to this team")
    if not found:
        await ctx.send(user.mention + " you do not have a valid invite to this team")
@client.command()
async def colourchange(ctx, teamname: discord.Role, color: discord.Colour):
    teams = teamscollection.find({"teamname": teamname})
    authors = user.id
    author = ctx.message.author.id
    for team in teams:
        try:
            team["teamname"]
        except:
            await ctx.send("This team does not exist")
        if authors in team["players"]:
            if teamname == team["teamname"]:
                roleold = discord.utils.get(ctx.guild.roles, name=teamname)
                await roleold.edit(colour = color)
                await ctx.send(ctx.message.author.mention + " colour has been changed")
                return 0
@client.command()
async def create(ctx, teamname): # working with mongo
    user= ctx.message.author
    authors = user.id
    teams = teamscollection.find({"teamname": teamname})
    for team in teams:
        try:
            team["teamname"]
            await ctx.send("Team name: " + teamname + " already exists, please choose another team name")
            return 0
        except:
            ''
    playerstatus = teamscollection.find({"players": user.id})
    print(playerstatus)
    for player in playerstatus:      
        await ctx.send(user.mention+ " You are already in another team")
        return 0
    guild = ctx.guild
    await guild.create_role(name=teamname, colour = discord.Colour(287371), hoist = 1, mentionable = True)
    role = discord.utils.get(ctx.guild.roles, name=teamname)
    await user.add_roles(role)
    teamscollection.insert_one({"teamname": teamname, "players": [user.id], "playersobj": [user.mention], "invites": [], "scrimpartners": [], "pendingscrimpartners": [], "teamrole": role.mention})
    print(role.mention)
@client.command()
async def invite(ctx, teamname, user: discord.User): # working with mongo
    teams = teamscollection.find({"teamname": teamname})
    authors = user.id
    author = ctx.message.author.id
    for team in teams:
        try:
            team["teamname"]
        except:
            await ctx.send("This team does not exist")
        if authors in team["players"]:
            await ctx.send("User is already in team: " + teamname)
            return 0
        if author in team["players"]:
            ''
        else:
            await ctx.send(ctx.message.author.mention+ " You are not in this team")
            return 0
            
    pendings = teamscollection.find({"teamname" : teamname})
    for pendinginvite in pendings:
        try:
            if user.id in pendinginvite["invites"]:
                await ctx.send(user.mention  + " Has already been invited to the team, please type !accept " + '"' + teamname + '"' + " to join the team")
                return 0
            msg = await ctx.send( user.mention + " You have been invited to join: " + teamname + " by: " + str(ctx.message.author) + ". Type !accept " + '"teamname"' + " to join the team")
            a=  pendinginvite["invites"]
            a.append(user.id)
            newvalues = { "$set": { "invites": a } }
            teamscollection.update_one({"teamname": teamname}, newvalues)         
        except:
            return 0
@client.command()
async def leave(ctx, teamname):  # working with mongo
    authorID = ctx.message.author.id
    data = teamscollection.find({"teamname": teamname})
    role = discord.utils.get(ctx.guild.roles, name=teamname)
    for teams in data:
        if authorID in teams["players"]:
            a = teams["players"]
            a.remove(authorID)
            await ctx.send(ctx.message.author.mention + " You have left " + teamname)
            if len(teams["players"]) == 0:
                for partners in teams["scrimpartners"]:
                    data = teamscollection.find({"teamrole": partners})
                    for team in data:
                        a = team["scrimpartners"]
                        a.remove(teams[teamrole])
                        update ={ "$set": { "scrimpartners": a } }
                        teamscollection.update_one({"teamrole": partners}, update)

                teamscollection.delete_one({"teamname": teamname})
                role = discord.utils.get(ctx.guild.roles, name=teamname)

                await role.delete(reason = None)
                await ctx.send("Team has been disbanded")
                return 0
            else:
                await ctx.message.author.remove_roles(role)
                update ={ "$set": { "players": a } }
                teamscollection.update_one({"teamname": teamname}, update)
                a = teams["playersobj"]
                a.remove(ctx.message.author.mention)
                update ={ "$set": { "players": a } }
                teamscollection.update_one({"teamname": teamname}, update)
                return 0
        else:
            await ctx.send("You are not in this team")
            return 0
    await ctx.send("Team: " + teamname + " does not exist")
    '''
@client.command()
async def kick(ctx, teamname ,user: discord.Member): # I think it works
    data = teamscollection.find({"teamname": teamname})
    for team in data:
        if user.id in team["players"] and ctx.message.author.id in team["players"]:
            role = discord.utils.get(ctx.guild.roles, name=teamname)
            await user.remove_roles(role)
            a = team["players"]
            a.remove(user.id)
            update ={ "$set": { "players": a } }
            teamscollection.update_one({"teamname": teamname}, update)
            a = team["playersobjs"]
            a.remove(user.mention)
            update = { "$set": { "playersobjs": a}}
            teamscollection.update_one({"teamname": teamname}, update)

            await ctx.send(user.mention + " has been removed from " + teamname)
            return 0
    await ctx.send(ctx.message.author.mention +" you are not in the same team as " + user.mention+ " or the team doesnt exist")

    '''
@client.command()
async def teams(ctx):  # Works with mongo
    output = ''
    teams = teamscollection.find({})
    for team in teams:
        output += team["teamname"] + "\n"
    await ctx.send(output)

@client.command()
async def team(ctx, teamname):  # Works with mongo
    output = ''
    teams  = teamscollection.find({"teamname": teamname})
    for users in teams:
        players = users["players"]
        for i in range(len(players)):
            user = await client.fetch_user(players[i])
            output += user.name+ "\n"
    await ctx.send(output)
@client.command()
async def acreate(ctx, teamname, player1: discord.Member, player2: discord.Member, player3: discord.Member, color):  # Doesnt care for people being in multiple teams as this is a sdmni force through
    # This function works with mongo
    perms = ctx.message.author.id
    admins = db["admins"]
    query = admins.find({str(perms): "Admin"})
    for perms in query:
        user= ctx.message.author
        authors = user.id
        teams = teamscollection.find({"teamname": teamname})
        for team in teams:
            try:
                team["teamname"]
                await ctx.send("Team name: " + teamname + " already exists, please choose another team name")
                return 0
            except:
                ''
        guild = ctx.guild
        await guild.create_role(name=teamname, colour = discord.Color(int(color)), hoist = 1, mentionable = 1)

        role = discord.utils.get(ctx.guild.roles, name=teamname)
        teamscollection.insert_one({"teamname": teamname, "players": [player1.id, player2.id, player3.id],"playersobjs": [player1.mention, player2.mention, player3.mention], "invites": [], "scrimpartners": [],
                                   "pendingscrimpartners": [], "teamrole": role})
        
        await player1.add_roles(role)
        await player2.add_roles(role)
        await player3.add_roles(role)
        await ctx.send("Team has been created")

        
    else:
        return 0

        

@client.command()
async def admin(ctx, user: discord.User):  # works in morgo
    admins = db["admins"]
    query = admins.find({str(ctx.message.author.id ): "Admin"})
    for perms in query:
        admins.insert_one({str(user.id): "Admin"})    
        await ctx.send("admin created")

@client.command()
async def aadd(ctx, teamname, player1: discord.Member):
    admins = db["admins"]
    author = ctx.message.author.id
    query = admins.find({str(ctx.message.author.id): "Admin"})
    for author in query:
        print("a")
        teams =teamscollection.find({"teamname": teamname})
        for team in teams:
            a = team["players"]
            a.append(player1.id)
            newb = { "$set": { "players": a } }
            teamscollection.update_one( {"teamname" : teamname} , newb)

            a = team["playersobj"]
            a.append(player1.mention)
            newb = { "$set": { "playersobj": a } }
            teamscollection.update_one( {"teamname" : teamname} , newb)
            await ctx.send(player1.mention + " had been added to team: " + teamname)
            role = discord.utils.get(ctx.guild.roles, name=teamname)
            await player1.add_roles(role)
@client.command()
async def aremove(ctx, teamname, player1: discord.User):  # Works with mongo
    admins = db["admins"]
    author = ctx.message.author.id
    query = admins.find({str(ctx.message.author.id): "Admin"})
    for author in query:
        data = teamscollection.find({"teamname": teamname})
        for team in data:
            if player1.id in team["players"]:
                role = discord.utils.get(ctx.guild.roles, name=teamname)
                await player1.remove_roles(role)
                a = team["players"]
                a.remove(player1.id)
                b = team["playersobj"]
                b.remove(player1.mention)
                update ={ "$set": { "players": a } }
                updateb =   update ={ "$set": { "playersobj": b } }
                teamscollection.update_one({"teamname": teamname}, update)
                teamscollection.update_one({"teamname": teamname}, updateb)

                await ctx.send(player1.mention + " has been removed from " + teamname)
                return 0

    
@client.command()
async def adelete(ctx, teamname): #done
    admins = db["admins"]
    author = ctx.message.author.id
    query = admins.find({str(ctx.message.author.id): "Admin"})
    for author in query:
        data = teamscollection.find({"teamname": teamname})
        for team in data:    
            await ctx.send(teamname + " has been removed")
            teamscollection.delete_one({"teamname": teamname})
            role = discord.utils.get(ctx.guild.roles, name=teamname)
            await role.delete(reason = None)           
@client.command()
async def commands(ctx):
    string = ""
    for elements in command:
        string= string + elements + "\n"
    await ctx.send(string)
    return 0
@client.command()
async def scrimpartner(ctx, teamrole):
     authorID = ctx.message.author.id
     data = teamscollection.find({})
     print(authorID)
     for teams in data:
         if authorID in teams["players"]:
             print("in team")
             if teamrole in teams["pendingscrimpartners"]:
                 print("nope")
                 if teamrole in teams["scrimpartners"]:
                    await ctx.send("You are already scrim partners")
                    return 0
                 print("yeet")
                 otherteam = teamscollection.find({"teamrole": teamrole})
                 for team in otherteam:            
                     a = team["scrimpartners"]
                     a.append(teams["teamrole"])
                     newa = { "$set": { "scrimpartners": a } }
                     teamscollection.update_one( {"teamrole" : team["teamrole"]} , newa)
                     b = teams["scrimpartners"]
                     b.append(team["teamrole"])
                     newb = { "$set": { "scrimpartners": b } }
                     teamscollection.update_one( {"teamrole" : teams["teamrole"]} , newb)
                     await ctx.send(teamname +" and " + teams["teamrole"]+ " are now scrim partners")
                     return 0
             else:
                otherteam = teamscollection.find({"teamrole": teamrole})
                for team in otherteam:
                    b = team["pendingscrimpartners"]
                    b.append(teams["teamrole"])
                    newb = { "$set": { "pendingscrimpartners": b } }
                    teamscollection.update_one( {"teamrole" : team["teamrole"]} , newb)

                    await ctx.send(teamrole + " If you would like to be scrim partners type !scrimpartner @" + teams["teamname"] )
                    return 0
     await ctx.send("Sorry you are not in a team and are unable to become scrim partners. To join a team type !create teamname")
    
@client.command()
async def scrimnow(ctx):
    authorID = ctx.message.author.id
    data = teamscollection.find({})
    for teams in data:
         if authorID in teams["players"]:
             teamslist = []
             string = ''
             for teamspart in teams["scrimpartners"]:
                 string= string+" "+ teamspart
             print(string)
             string2 = ''
             for players in teams["playersobj"]:
                 info = players
                 string2 = string2 + " " +info
             await ctx.send(string + " " + teams["teamname"] + " are now looking for a scrim DM" + string2)

@client.command()
async def scrimlater(ctx, time, timezone):
    authorID = ctx.message.author.id
    data = teamscollection.find({})
    for teams in data:
         if authorID in teams["players"]:
             mention = teams["teamrole"]
             times = ["AWST", "ACST", "AEST", "AEDT", "NZST", "NZDT"]
             string2 = ''
             for players in teams["playersobj"]:
                 info = players
                 string2 = string2 + " " +info
             if timezone.upper() in times:
                 await ctx.send("Team " + mention+ " Is looking for a scrim at " + time + " " + timezone + " DM " + string2 )
                 return 0
             else:
                 await ctx.send("Invalid time zone")
                 return 0
    await ctx.send("Error you are not in a team")
'''
@client.command()
async def gay(ctx):
    await ctx.send("<@292471409106747392>")
    '''
client.run("NjEwNzA0OTg0NDg0MzQ3OTE0.XVJMaQ.jd1dvq9yy5Wf9bOC8i9VuSs3hJo")

