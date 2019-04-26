# -*- coding: utf-8 -*-
import os
import telebot
import time
import random
import threading
from emoji import emojize
from telebot import types
from pymongo import MongoClient
import traceback

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)


games={}

def effect(target='all', amount=0):
      return {
          'target':target,
          'amount':amount
      }
    

coldunstva={
    'start':{},
    'mid':{},
    'end':{}
}
cstart={'Ебанутый':{
    'effects':{'damage':effect(target='all', amount=2)
              },
    'cost':47
                },
         
        'Ебущий':{
    'effects':{'damage':effect(target='allenemy', amount=1),
               'stun':effect(target='1random', amount=1)
              },
    'cost':47

                 }
          
       }

cmid={'Осёл':{
    'effects':{'damage':effect(target='allenemy', amount=3)
              },
    'cost':47
                },
         
        'Пидорас':{
    'effects':{'heal':effect(target='self', amount=2),
               'stun':effect(target='1random', amount=1)
              },
    'cost':47

                 }
          
       }

cend={'С нижнего Тагила':{
    'effects':{'heal':effect(target='all', amount=1)
              },
    'cost':47
                },
         
        'Дряхлой бабки':{
    'effects':{'stun':effect(target='2random', amount=2)
              },
    'cost':47

                 }
          
       }

for ids in cstart:
    coldunstva['start'].update({ids:cstart[ids]})
for ids in cmid:
    coldunstva['mid'].update({ids:cmid[ids]})
for ids in cend:
    coldunstva['end'].update({ids:cend[ids]})
    

    
@bot.message_handler(commands=['coldunstvo'])
def coldovatt(m):
    if m.chat.id not in games:
        games.update(creategame(m.chat.id))
        bot.send_message(m.chat.id, 'Го колдовать, я создал\n/joen для присоединения.')
    
@bot.message_handler(commands=['joen'])
def coldovattjoen(m):
    try:
        if m.from_user.id not in games[m.chat.id]['players'] and games[m.chat.id]['started']==False:
            games[m.chat.id]['players'].update(createplayer(m.from_user))
            bot.send_message(m.chat.id, m.from_user.first_name+' присоединился!')
    except:
        bot.send_message(m.chat.id, 'Тут еще нет игры ебать.')
        bot.send_message(441399484, traceback.format_exc())
        
        
@bot.message_handler(commands=['gogogo'])
def coldovattstart(m):
    try:
        games[m.chat.id]['started']=True
        bot.send_message(m.chat.id, 'ПОИХАЛИ КОЛДОВАТЬ!')
        begincoldun(m.chat.id)
    except:
        bot.send_message(m.chat.id, 'Здесь нет игры ебать!')
        bot.send_message(441399484, traceback.format_exc())
            
    
    
def begincoldun(id):
    game=games[id]
    for ids in game['players']:
        player=game['players'][ids]
        if 'stunned' not in player['effects'] and player['hp']>0:
            turn(game, player)
    bot.send_message(id, game['endturntext'])
    game['endturntext']=''
    alive=0
    for ids in game['players']:
        player=game['players'][ids]
        if player['hp']>0:
            alive+=1
    if alive<=1:
        endgame(game)
    else:
        t=threading.Timer(10, begincoldun, args=[id])
        t.start()
    
def endgame(game):
    text='Игра окончена! Выжившие:\n'
    for ids in game['players']:
        player=game['players'][ids]
        if player['hp']>0:
            alivetext+=player['name']+'\n'
    if text=='Игра окончена! Выжившие:\n':
        text+='Выживших нет! ВСЕ СДОХЛИ НАХУУУЙ!'
    bot.send_message(game['id'], text)
    del games[game['id']]
    
    
def turn(game, player):
    allcs=[]
    allcm=[]
    allce=[]
    for i in coldunstva['start']:
        print('i=')
        print(i)
        print(coldunstva['start'][i])
        allcs.append(coldunstva['start'][i])
    for i in coldunstva['mid']:
        allcm.append(coldunstva['mid'][i])
    for i in coldunstva['end']:
        allce.append(coldunstva['end'][i])
    start=random.choice(allcs)
    mid=random.choice(allcm)
    end=random.choice(allce)
    zaklinanie={
        'start':start,
        'mid':mid,
        'end':end
    }
    effecttext=''
    for ids in zaklinanie:
        print(zaklinanie)
        effecttext+=cast(zaklinanie[ids], game, player)
        zakltext+=ids+' '
    game['endturntext']+='Ход игрока '+player['name']+'! Он кастует: '+zakltext+'! Вот, что он сделал:\n'+effecttext+'\n'
    
    
def cast(zaklinanie, game, player):
    text=''
    print(zaklinanie)
    for ids in zaklinanie:
        name=ids
    for ids in zaklinanie['effects']:
        effect=zaklinanie['effects'][ids]
        if ids=='damage':
            if effect['target']=='all':
                text+='Нанёс всем '+str(effect['amount'])+' урона!\n'
                for idss in game['players']:
                    target=game['players'][idss]
                    target['hp']-=effect['amount']
            elif effect['target']=='allenemy':
                text+='Нанёс всем своим врагам '+str(effect['amount'])+' урона!\n'
                for idss in game['players']:
                    target=game['players'][idss]
                    if target['id']!=player['id']:
                        target['hp']-=effect['amount']
                        
            elif 'random' in effect['target']:
                if 'enemy' not in effect['target']:
                    amount=int(effect['target'].split('random')[0])
                    i=0
                    text+='Нанес '+str(effect['amount'])+' урона колдунам:\n'
                    while i<amount:
                        target=random.choice(game['players'])
                        target['hp']-=effect['amount']
                        text+=target['name']+'\n'
                        i+=1
                else:
                    amount=int(effect['target'].split('random')[0])
                    i=0
                    text+='Нанес '+str(effect['amount'])+' урона соперникам:\n'
                    while i<amount:
                        target=random.choice(game['players'])
                        while target['id']==player['id']:
                            target=random.choice(game['players'])
                        target['hp']-=effect['amount']
                        text+=target['name']+'\n'
                        i+=1
        if ids=='heal':
            if effect['target']=='all':
                text+='Восстановил '+str(effect['amount'])+' хп всем участникам боя!\n'
                for idss in game['players']:
                    target=game['players'][idss]
                    target['hp']+=effect['amount']
                    
            elif effect['target']=='allenemy':
                text+='Восстановил '+str(effect['amount'])+' хп всем своим врагам (непонятно, для чего. Возможно, он еблан)!\n'
                for idss in game['players']:
                    target=game['players'][idss]
                    if target['id']!=player['id']:
                        target['hp']-=effect['amount']
            
            elif effect['target']=='self':
                text+='Восстановил себе '+str(effect['amount'])+' хп!\n'
                player['hp']+=effect['amount']
                
            elif 'random' in effect['target']:
                if 'enemy' not in effect['target']:
                    amount=int(effect['target'].split('random')[0])
                    i=0
                    text+='Восстановил '+str(effect['amount'])+' хп колдунам:\n'
                    while i<amount:
                        target=random.choice(game['players'])
                        target['hp']+=effect['amount']
                        text+=target['name']+'\n'
                        i+=1
                else:
                    amount=int(effect['target'].split('random')[0])
                    i=0
                    text+='Восстановил '+str(effect['amount'])+' хп соперникам:\n'
                    while i<amount:
                        target=random.choice(game['players'])
                        while target['id']==player['id']:
                            target=random.choice(game['players'])
                        target['hp']-=effect['amount']
                        text+=target['name']+'\n'
                        i+=1
                
        if ids=='stun':
            if effect['target']=='all':
                text+='Застанил всех игроков на '+str(effect['amount'])+' ходов!\n'
                for idss in game['players']:
                    target=game['players'][idss]
                    i=0
                    while i<effect['amount']:
                        target['effects'].append('stun')
                        i+=1
                                
            elif effect['target']=='allenemy':
                text+='Застанил всех своих врагов на '+str(effect['amount'])+' ходов!\n'
                for idss in game['players']:
                    target=game['players'][idss]
                    if target['id']!=player['id']:
                        i=0
                        while i<effect['amount']:
                            target['effects'].append('stun')
                            i+=1
            
            elif effect['target']=='self':
                text+='Застанил себя на '+str(effect['amount'])+' ходов! Ебланище.\n'
                i=0
                while i<effect['amount']:
                    player['effects'].append('stun')
                    i+=1
                
            elif 'random' in effect['target']:
                if 'enemy' not in effect['target']:
                    amount=int(effect['target'].split('random')[0])
                    i=0
                    text+='Застанил '+str(amount)+' колдунов на '+str(effect['amount'])+' ходов. Пострадавшие:\n'
                    while i<amount:
                        target=random.choice(game['players'])
                        target['hp']-=effect['amount']
                        text+=target['name']+'\n'
                        i+=1
                else:
                    amount=int(effect['target'].split('random')[0])
                    i=0
                    text+='Застанил '+str(amount)+' соперников на '+str(effect['amount'])+' ходов. Пострадавшие:\n'
                    while i<amount:
                        target=random.choice(game['players'])
                        while target['id']==player['id']:
                            target=random.choice(game['players'])
                        target['hp']-=effect['amount']
                        text+=target['name']+'\n'
                        i+=1
                
    return text
    
    
def creategame(chatid):
    return {chatid:{
        'id':chatid,
        'players':{},
        'started':False,
        'endturntext':''
    }}

def createplayer(user):
    return {user.id:{
        'id':user.id,
        'hp':20,
        'effects':[]
    }
           }

print('7777')
bot.polling(none_stop=True,timeout=600)

