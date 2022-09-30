import asyncio
import discord
import random
from discord.ext import commands
from utils import send_embed,field,config_dict
import math
from concurrent.futures import ThreadPoolExecutor

botName=config_dict['botName']
class tictactoe():
    def __init__(self):
        self.game_matrix=self.make_game_matrix()

    @staticmethod
    def make_game_matrix():
        return [[-2]*3 for i in range(3)]
    
    def get_free_spots(self):
        free_slots=[]
        for i in range(3):
            for j in range(3):
                if self.game_matrix[i][j]==-2:
                    free_slots.append(1+j+3*i)
        return free_slots

    def has_won(self):
        for i in range(3):
            j=0
            if self.game_matrix[i][j]==self.game_matrix[i][j+1]==self.game_matrix[i][j+2] and self.game_matrix[i][j]!=-2:
                return {'has_won':True,'winner':self.game_matrix[i][j]}
        for j in range(3):
            i=0
            if self.game_matrix[i][j]==self.game_matrix[i+1][j]==self.game_matrix[i+2][j] and self.game_matrix[i][j]!=-2:
                return {'has_won':True,'winner': self.game_matrix[i][j]}
        if self.game_matrix[0][0]==self.game_matrix[1][1]==self.game_matrix[2][2] and self.game_matrix[1][1]!=-2:
            return {'has_won':True,'winner':self.game_matrix[0][0]}
        if self.game_matrix[2][0]==self.game_matrix[1][1]==self.game_matrix[0][2] and self.game_matrix[1][1]!=-2:
            return {'has_won':True,'winner':self.game_matrix[2][0]}
        return {'has_won':False,'winner':None}
    
    def is_finished(self):
        for i in range(3):
            for j in range(3):
                if self.game_matrix[i][j]==-2:
                    return False
        return True
    
    def update_matrix(self,index,coin) -> None:
        lut={
            1:{
                'i':0,
                'j':0
            },
            2:{
                'i':0,
                'j':1
            },
            3:{
                'i':0,
                'j':2
            },
            4:{
                'i':1,
                'j':0
            },
            5:{
                'i':1,
                'j':1
            },
            6:{
                'i':1,
                'j':2
            },
            7:{
                'i':2,
                'j':0
            },
            8:{
                'i':2,
                'j':1
            },
            9:{
                'i':2,
                'j':2
            }
        }
        self.game_matrix[lut[index]['i']][lut[index]['j']]=coin
        # return game_matrix
    
class tictactoe_ai_player():
    def __init__(self,coin):
        self.coin=coin
    async def get_move(self,game: tictactoe):
        free_spots=game.get_free_spots()
        if len(free_spots)==9:
            return random.choice(free_spots)
        elif len(free_spots)==8:
            if (1 not in free_spots) or (3 not in free_spots) or (7 not in free_spots) or (9 not in free_spots):
                return 5
            elif 5 not in free_spots:
                return 1
            elif (2 not in free_spots) or (4 not in free_spots):
                return 1
            else:
                return 9
        else:
            loop=asyncio.get_event_loop()
            move=await loop.run_in_executor(ThreadPoolExecutor(),self.minimax,game,self.coin)
            return move['position']
    
    def minimax(self,game: tictactoe,player):
        max_player=self.coin
        opponent="X" if player=="O" else "O"
        
        if game.has_won()['winner']==opponent:
            return {'position':None,'score':1*(len(game.get_free_spots())+1) if opponent==max_player else (-1)*(len(game.get_free_spots())+1)}
        elif len(game.get_free_spots())==0:
            return {'position':None,'score':0}
        
        if player==max_player:
            best_move={'position':None,'score':-math.inf}
        else:
            best_move={'position':None,'score':math.inf}

        for spot in game.get_free_spots():
            game.update_matrix(spot,player)
            sim=self.minimax(game,opponent)
            game.update_matrix(spot,-2)
            sim['position']=spot

            if player==max_player:
                if sim['score']>best_move['score']:
                    best_move=sim
            else:
                if sim['score']<best_move['score']:
                    best_move=sim
        
        return best_move

class games(commands.Cog):
    def __init__(self,client):
        self.client=client
    
    async def send_playing(self,game_matrix,channel,player,opponent=None,self_win=False):
        description="\n"
        keycap_lut={
            1:'\U00000031'+'\U000020e3',
            2:'\U00000032'+'\U000020e3',
            3:'\U00000033'+'\U000020e3',
            4:'\U00000034'+'\U000020e3',
            5:'\U00000035'+'\U000020e3',
            6:'\U00000036'+'\U000020e3',
            7:'\U00000037'+'\U000020e3',
            8:'\U00000038'+'\U000020e3',
            9:'\U00000039'+'\U000020e3'
        }
        for i in range(3):
            for j in range(3):
                if game_matrix[i][j]!=-2:
                    if game_matrix[i][j]=="X":
                        description+="\U0000274c"
                    if game_matrix[i][j]=="O":
                        description+="\U00002b55"
                else:
                    description+=keycap_lut[1+j+3*i]
            description+="\n"
        await send_embed(channel,f"Tic-Tac-Toe: {player.name} Vs {opponent.name if opponent!=None else botName}",description,fields=[field(f'Your turn, {player.name}','Enter the number corresponding to the spot you would like to mark.')] if not self_win else None,footer="clear")

    async def wait_msg(self,author,channel,timeout=20):
        try:
            resp=await self.client.wait_for('message',check=lambda resp: resp.author==author and resp.channel==channel,timeout=timeout)
        except asyncio.TimeoutError:
            await channel.send("Request Timeout.")
            return False
        else:
            print("Got Resp")
            return resp
    
    async def game_run(self,ctx):
        #Prompt for who goes first
        await send_embed(ctx.channel,f"Tic-Tac-Toe: {ctx.author.name} Vs {botName}","Would you like to go first?",footer="Reply with Y or N.")
        resp=await self.wait_msg(ctx.author,ctx.channel)
        
        #Checking who goes first.
        if resp.content=="Y" or resp.content=="y" or resp.content=="Yes" or resp.content=="yes":
            me=tictactoe_ai_player("O")
            player_coin="X"
        elif resp==False:
            return
        else:
            await ctx.send("I'm going first.")
            me=tictactoe_ai_player("X")
            player_coin="O"
        
        #initialising game
        game=tictactoe()
        completed=False
        
        #Bot plays first move if its going first
        if me.coin=="X":
            index=await me.get_move(game)
            game.update_matrix(index,"X")
        
        #Main Game Loop
        while not completed:
            print("Looped")
            
            #Sending current game state and awaiting move
            await self.send_playing(game.game_matrix,ctx.channel,ctx.author)
            resp=await self.wait_msg(ctx.author,ctx.channel)
            
            #Response Validity Check
            if not resp:
                completed=True
                break
            else:
                print("Entered with Resp: ",resp.content)
                try:
                    index=int(resp.content[0])
                    free_spots=game.get_free_spots()
                    #Move Validity Check
                    if index in free_spots:
                        game.update_matrix(int(resp.content[0]),player_coin)
                    else:
                        await ctx.send("That move has already been played.")
                        continue
                except:
                    await ctx.send("Invalid character, expected a number between 1-9.")
                    raise
                
                # print("Updated Game Matrix:")
                # print(game.game_matrix)
                
                win_status=game.has_won()
                win_bool=win_status['has_won']
                winner=win_status['winner']
                
                # print("Checked if Won: ",win_bool)
                
                if not win_bool:
                    #Hasn't Won, Game still playing
                    # print("Entered Still Playing Fork")
                    
                    if not game.is_finished():
                        #Not Draw
                        # print("Not Finished")
                        
                        #BotMove
                        index=await me.get_move(game)
                        game.update_matrix(index,me.coin)
                        
                        # print("Updated Game Matrix:")
                        # print(game.game_matrix)
                        
                        self_win_status=game.has_won()
                        if self_win_status['has_won'] and self_win_status['winner']==me.coin:
                            #BotWon
                            await self.send_playing(game.game_matrix,ctx.channel,ctx.author,None,True)
                            await send_embed(ctx.channel,"Aw Snap!","I beat you!",discord.Colour.red(),footer='clear')
                            completed=True
                            break
                        elif game.is_finished():
                            #draw
                            # print("Drawed")
                            await self.send_playing(game.game_matrix,ctx.channel,ctx.author,None,True)
                            await send_embed(ctx.channel,"Huh...?","That's non-binary.\n Oh this must be what humans call a **Draw**!",discord.Colour.light_grey(),footer='clear')
                            completed=True
                            break
                    else:
                        #draw
                        # print("Drawed")
                        await send_embed(ctx.channel,"Huh...?","That's non-binary.\n Oh this must be what humans call a **Draw**!",discord.Colour.light_grey(),footer='clear')
                        completed=True
                        break
                elif win_bool and winner==player_coin:
                    #PlayerWon
                    await send_embed(ctx.channel,"Congratulations","You beat me!",discord.Colour.green(),footer='clear')
                    completed=True
                    break
                elif win_bool and winner==me.coin:
                    #BotWon
                    await send_embed(ctx.channel,"Aw Snap!","I beat you!",discord.Colour.red(),footer='clear')
                    completed=True
                    break
                else:
                    #error
                    print("Error")
                    return
    
    async def game_2player_run(self,ctx,player1,player2):
        game=tictactoe()
        completed=False
        current_player=player1
        while not completed:
            print("Looped")
            await self.send_playing(game.game_matrix,ctx.channel,current_player,player1 if current_player==player2 else player2)
            resp=await self.wait_msg(current_player,ctx.channel)
            if not resp:
                await ctx.send(f"{current_player.mention} did not respond. Why though?")
                completed=True
                break
            else:
                print("Entered with Resp: ",resp.content)
                try:
                    game.update_matrix(int(resp.content[0]),"X" if current_player==player1 else "O")
                except:
                    await ctx.send("Invalid character, expected a number between 1-9.")
                    raise
                print("Updated Game Matrix:")
                print(game.game_matrix)
                win_status=game.has_won()
                win_bool=win_status['has_won']
                winner=win_status['winner']
                print("Checked if Won: ",win_bool)
                if not win_bool:
                    print("Entered Still Playing Fork")
                    if not game.is_finished():
                        print("Not Finished")
                    else:
                        #draw
                        print("Drawed")
                        await send_embed(ctx.channel,"Huh...?","That's non-binary.\n Oh this must be what humans call a **Draw**!",discord.Colour.light_grey(),footer='clear')
                        completed=True
                        break
                elif win_bool and winner=="X":
                    #PlayerWon
                    await send_embed(ctx.channel,f"Congratulations {player1.name}",f"You've Won!\nYou beat {player2.name}!",discord.Colour.green(),footer='clear')
                    completed=True
                    break
                elif win_bool and winner=="O":
                    #BotWon
                    await send_embed(ctx.channel,"Aw Snap!",f"It seems like {player2.name} has beat you, {player1.name}.",discord.Colour.red(),footer='clear')
                    completed=True
                    break
                else:
                    #error
                    print("Error")
                    return
                current_player=player2 if current_player==player1 else player1

    @commands.command(help="Plays Tic-Tac-Toe.",aliases=['tic-tac-toe'])
    async def tictactoe(self,ctx,player2: discord.Member=None):
        if player2==None:
            await self.game_run(ctx)
        elif isinstance(player2,discord.Member):
            if player2.bot==0:
                player1=ctx.author
                await self.game_2player_run(ctx,player1,player2)
            else:
                if player2.name==botName:
                    await self.game_run(ctx)
                else:
                    await ctx.send("You cannot play with a Bot.")
                    
        
    
async def setup(client):
    await client.add_cog(games(client))