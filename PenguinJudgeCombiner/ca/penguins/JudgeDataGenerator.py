import requests
from bs4 import BeautifulSoup
import csv
from astropy.table import index
#Note: Number, Name, Tournament Rank, Skills Rank, Judged Score, wlt, wp, ap, sp, total skills, prog, driving, prog attempts, driving attempts ----
'''
Created on May 25, 2020

@author: kaide
'''
#Vex Team Database Management ------------------------------------------------------------------------------------------------------
class CompetingTeam:

    def __init__(self, number):
        #From Rankings Page
        self.team_number = number #Actually String ###X
        self.name = "" #String
        
        self.rank = 0 #Integer
        self.wlt = "x-x-x" #String
        self.wp = 0 #Integer
        self.ap = 0 #Integer
        self.sp = 0 #Integer
        
        #From Skills Page
        self.skills_rank = 0 #Number
        self.skills_score = 0 #Number
        self.prog_score = 0 #Number
        self.prog_attempts = 0 #Number
        self.driving_score = 0 #Number
        self.driving_attempts = 0 #Number
        
        #Judges Information
        self.judge_score = 0 #Number
        self.has_judged_score = False #Boolean
        
    def get_number(self):
        return self.team_number
    
    def set_name(self, name):
        self.name = name
    
    def set_rank(self, rank):
        self.rank = rank
    
    def set_wlt(self, nwlt):
        self.wlt = nwlt
    
    def set_wp(self, wp):
        self.wp = wp
    
    def set_ap(self, ap):
        self.ap = ap
    
    def set_sp(self, sp):
        self.sp = sp
    
    def set_skills_rank(self, skillsrank):
        #print("Set skills rank for team", self.team_number, "to", skillsrank)
        self.skills_rank = skillsrank
    
    def set_skills_score(self, skillscore):
        self.skills_score = skillscore
    
    def set_prog_score(self, progscore):
        self.prog_score = progscore
    
    def set_drive_score(self, drivescore):
        self.driving_score = drivescore
    
    def set_prog_attempts(self, progattempts):
        self.prog_attempts = progattempts
    
    def set_drive_attempts(self, driveattempts):
        self.driving_attempts = driveattempts
    
    def set_judge_score(self, judgescore):
        self.judge_score = judgescore
        self.has_judged_score = True
        
    def get_judged_score(self):
        return self.judge_score
        
    def to_html(self):
        return "<tr><td>" + str(self.team_number) + "</td><td>" + str(self.rank) + "</td><td>" + str(self.judge_score) + "</td></tr>"
    
    def to_csv(self):
        return str(self.team_number) + "," + self.rank + "," + self.skills_rank + "," + self.judge_score
    
    def data_to_list(self):
        return [self.team_number, self.name, self.rank, self.skills_rank, self.judge_score, \
                self.wlt, self.wp, self.ap, self.sp, self.skills_score, self.prog_score, \
                self.driving_score, self.prog_attempts, self.driving_attempts]
    
    def get_has_judged_score(self):
        return self.has_judged_score

#module componenets
teams = {}

def add_team(team):
    if not team.get_number() in teams:
        teams[team.get_number()] = team

def add_judged_score(number, score):
    if not number in teams:
        teams[number] = CompetingTeam(number)
    teams[number].set_judge_score(score)

def add_rank(number, rank):
    if not number in teams:
        teams[number] = CompetingTeam(number)
        teams[number].set_judge_score(0)
    teams[number].set_rank(rank)

def add_skills_rank(number, srank):
    if not number in teams:
        teams[number] = CompetingTeam(number)
    teams[number].set_skills_rank(srank)

# Web Scraping Module ----------------------------------------------------------------------------------------------------------
ROOT = "http://10.0.0.217/"
TOURNY = ROOT + "division1/rankings"
SKILLS = ROOT + "skills/rankings"
DIRECTORY = "D:/Penguin Judging Service/"
INPUT_FILE = DIRECTORY + "teams.csv"
OUTPUT_FILE = DIRECTORY + "combined.csv"

#Offsets to make lists easier ----------------------------------------
def number_offset(index):
    return index+1

def name_offset(index):
    return index+2

def rank_index(index):
    return index

def wlt_offset(index):
    return index+3

def wp_offset(index):
    return index+4

def ap_offset(index):
    return index+5

def sp_offset(index):
    return index+6

def score_offset(index):
    return index+3

def prog_score_offset(index):
    return index+4

def drive_score_offset(index):
    return index+6

def prog_attempt_offset(index):
    return index+5

def drive_attempt_offset(index):
    return index+7
#End offsets ----


#Converts the HTML elements into raw strings for processing
def preprocess_elms(elms):
    converted = []
    for raw in elms:
        converted.append(raw.get_text())
    return converted

def get_tourny_rank():
    page = requests.get(TOURNY)
    soup = BeautifulSoup(page.content, 'html.parser')
    tableElms = soup.find_all('td')
    
    #print(tableElms)
    #print(preprocess_elms(tableElms))
    
    elms = preprocess_elms(tableElms)
    
    for index in range(0, len(tableElms), 7):
        add_rank(elms[number_offset(index)], elms[index]) #Guarentess the team exists now
        team = teams[elms[number_offset(index)]] #Get a ref
        
        team.set_name(elms[name_offset(index)])
        team.set_wlt(elms[wlt_offset(index)])
        team.set_wp(elms[wp_offset(index)])
        team.set_ap(elms[ap_offset(index)])
        team.set_sp(elms[sp_offset(index)])

def get_skills_ranks():
    page = requests.get(SKILLS)
    soup = BeautifulSoup(page.content, 'html.parser')
    tableElms = soup.find_all('td')
    
    elms = preprocess_elms(tableElms)
    
    for index in range(0, len(tableElms), 8):
        add_skills_rank(elms[number_offset(index)], elms[index]) #Guarentees existance
        
        team = teams[elms[number_offset(index)]]
        team.set_skills_score(elms[score_offset(index)])
        team.set_prog_score(elms[prog_score_offset(index)])
        team.set_drive_score(elms[drive_score_offset(index)])
        team.set_prog_attempts(elms[prog_attempt_offset(index)])
        team.set_drive_attempts(elms[drive_attempt_offset(index)])

def load_judged_scores():
    with open(INPUT_FILE) as csv_file:
        print("Opened File")
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        print("CSV Reader Created")
        #print(csv_reader)
        for row in csv_reader:
            #print(f'\t{row[0]} judge score {row[1]}.')
            add_judged_score(row[0], row[1])
            line_count += 1
        print(f'Processed {line_count} lines.')

def save_combined_scores():
    with open(OUTPUT_FILE, mode='w', newline='') as team_scores:
        print("Opened Write File")
        team_writer = csv.writer(team_scores, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #Title Row
        team_writer.writerow(['Team Number', 'Team Name', 'Qualification Rank', 'Skills Rank', 'Judged Score', \
                              'WLT', 'WP', 'AP', 'SP', 'Skills Score', 'Programming Score', 'Driving Score', \
                              'Programming Attempts', 'Driving Attempts'])
        
        for team in teams:
            if teams[team].get_has_judged_score() and teams[team].get_judged_score() != 0:
                team_writer.writerow(teams[team].data_to_list())
    print("Done Write")

#Main Executing Stuff ---------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    load_judged_scores()
    get_tourny_rank()
    get_skills_ranks()
    save_combined_scores()
    print("Program Exiting")
