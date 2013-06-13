#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
from datetime import date

logname = "../data/20130424_064954.txt"
resultname = "result.txt"

pattern = { 'date': r'\d{4}\.\d\d\.\d\d',
            'time': r'\d\d\:\d\d\:\d\d',
            'type': r'\((.+)\)'}

fromword = u"来自"
toword = u"对"
missword = u'完全没有打中'
youword = u'你'

#newcampaign = true

#combats = []

class Campaign:
    def __init__(self):
        self.involver = ['you']
        self.damagedone = 0
        self.damagereceived = 0
        self.hitdone = 0
        self.miss = 0
        self.hitreceived = 0
        self.missed = 0
        self.detail = []

    def damage_to(self, enemy, point, weapon='unknown'):
        self.damagedone += point
        self.hitdone += 1
        self.add_involver(enemy)

    def damage_receive(self, enemy, point, weapon='unknown'):
        self.damagereceived += point
        self.hitreceived += 1
        self.add_involver(enemy)

    def miss_to(self, enemy):
        self.miss += 1
        self.add_involver(enemy)

    def miss_by(self, enemy):
        self.missed += 1
        self.add_involver(enemy)

    def add_involver(self, enemy):
        if enemy not in self.involver:
            self.involver.append(enemy)

def process_none_msg(line,current_campaign):
#    newcombat = true
    pass

def process_notify_msg(line,current_campaign):
    pass

def process_combat_msg(line,current_campaign):
#    if newcombat :
#        currentcombat = 
#    newcombat = false
    pattern = { 'point' : r"<b>(\d+)<\/b>",
                'dirc' : r"size=10>(.+)<\/font>",
                'enemy' : r"f{8}>([\s\S]*)<\/b>",
                'any' : r"[\s\S]*" }
    hit_pattern = pattern['point']
    hit_pattern += pattern['any']
    hit_pattern += pattern['dirc']
    hit_pattern += pattern['any']
    hit_pattern += pattern['enemy']
    match = re.search(hit_pattern,line)
    if match :
        point = match.group(1)
        dirc = match.group(2)
        enemy = match.group(3)
        if dirc.decode('utf-8') == fromword:
            current_campaign.damage_receive(enemy,int(point))
        elif dirc.decode('utf-8') == toword:
            current_campaign.damage_to(enemy,int(point))
#The following code is dirty hack to deal with the god damn non unicode encoding.
#TODO: improve it.
    else :
        message_pattern = u"\\) ([\\s\\S]*)\n"
        match = re.search(message_pattern,line)
        if match :
            message = match.group(1)
            message = message.decode('utf-8')
            miss_pattern = u"^([\\s\\S]*)"
            miss_pattern += missword
            miss_pattern += u"([\\s\\S]*)"
            match = re.search(miss_pattern,message)
            if match :
                gunner = match.group(1)
                target = match.group(2)
                if target == youword:
                    current_campaign.miss_by(gunner.encode('utf-8'))
                else:
                    current_campaign.miss_to(target.encode('utf-8'))

def process_question_msg(line,current_campaign):
    pass

process_function = { 'None': process_none_msg,
                     'notify': process_notify_msg,
                     'combat': process_combat_msg,
                     'question': process_question_msg }

current_campaign = Campaign()

for line in file(logname):
    match = re.search(pattern['type'],line)
    if match :
        type = match.group(1)
        if type in process_function:
            process_function[type](line,current_campaign)

f = open(resultname,'w')
f.write('involvers:' + str(len(current_campaign.involver)) + '\n')
for involver in current_campaign.involver:
    f.write(involver+' ')
f.write('\n')
f.write('total damage received:' + str(current_campaign.damagereceived)+ '\n' )
f.write('total damage done:' + str(current_campaign.damagedone) + '\n' )
f.write('total miss:' + str(current_campaign.miss) + '\n' )
f.write('total missed:' + str(current_campaign.missed) + '\n')
f.close()
