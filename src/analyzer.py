#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
from datetime import datetime

logname = "../data/20130527_095916.txt"
resultname = "result.txt"

type_pattern = r'\((.+)\)'

fromword = u"来自"
toword = u"对"
missword = u'完全没有打中'
youword = u'你'

#newcampaign = True

#combats = []

class Campaign:
    def __init__(self):
        self.starttime = None
        self.endtime = None
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

    def write_to_file(self, filename):
        f = open(filename,'w')
        f.write('start time:' + str(self.starttime)+'\n')
        f.write('end time:' + str(self.endtime)+'\n')
        f.write('involvers:' + str(len(self.involver)) + '\n')
        for involver in self.involver:
            f.write(involver+'|')
        f.write('\n')
        f.write('total damage received:' + str(self.damagereceived)+ '\n' )
        f.write('total damage done:' + str(self.damagedone) + '\n' )
        f.write('total hit:' + str(self.hitdone) + '\n')
        f.write('hits rate:' + str(self.hitdone*100/(self.hitdone+self.miss)) + '%\n')
        f.write('average damage:' + str(self.damagedone/self.hitdone) + '\n')
        f.write('total miss:' + str(self.miss) + '\n' )
        f.write('total missed:' + str(self.missed) + '\n')
        f.close()

def get_datetime(line):
    datetime_pattern = r'(\d{4})\.(\d\d).(\d\d) (\d\d):(\d\d):(\d\d)'
    match = re.search(datetime_pattern,line)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        hour = int(match.group(4))
        min = int(match.group(5))
        sec = int(match.group(6))
        dt = datetime(year,month,day,hour,min,sec)
        return dt
    else:
        return None

def process_none_msg(line,campaign):
#    newcombat = true
    pass

def process_notify_msg(line,campaign):
    pass

def process_combat_msg(line,campaign): 
    if not campaign.starttime:
        campaign.starttime = get_datetime(line)
    campaign.endtime = get_datetime(line)

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
    if match:
        point = match.group(1)
        dirc = match.group(2)
        enemy = match.group(3)
        if dirc.decode('utf-8') == fromword:
            campaign.damage_receive(enemy,int(point))
        elif dirc.decode('utf-8') == toword:
            campaign.damage_to(enemy,int(point))
    else:
        line = line.decode('utf-8')
        miss_pattern = u"\\) ([\\s\\S]*)"
        miss_pattern += missword
        miss_pattern += u"([\\s\\S]*)\n$"
        match = re.search(miss_pattern,line)
        if match :
            gunner = match.group(1)
            target = match.group(2)
            if target == youword:
                campaign.miss_by(gunner.encode('utf-8'))
            else:
                suffix_pattern = u"^([\\s\\S]*) - ([\\s\\S]*)$"
                match = re.search(suffix_pattern,target)
                if match:
                    target = match.group(1)
                campaign.miss_to(target.encode('utf-8'))

def process_question_msg(line,campaign):
    pass

process_function = { 'None': process_none_msg,
                     'notify': process_notify_msg,
                     'combat': process_combat_msg,
                     'question': process_question_msg }

current_campaign = Campaign()

for line in file(logname):
    match = re.search(type_pattern,line)
    if match :
        type = match.group(1)
        if type in process_function:
            process_function[type](line,current_campaign)

current_campaign.write_to_file(resultname)
