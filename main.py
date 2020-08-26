# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 00:39:31 2020

@author: itsme
"""

import pygame

from pygame import mixer

#Variables

WIDTH = 1200
HEIGHT = 600
BORDER = 20
VELOCITY = 3

#define classes

class Ball:
    RADIUS = 20
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        
    #Draw the ball on screen
    def show(self, color):
        global screen
        pygame.draw.circle(screen, color, (self.x, self.y), self.RADIUS)
    #Update the position of the ball        
    def update(self):
        global fgColor, bgColor, score_comp, score_user
        newx = self.x + self.vx
        newy = self.y + self.vy
        
        #bouncing effect sound
        bounce_effect = mixer.Sound('bounce_effect.wav')
        
        #check and update ball positions
        
        #hitting computer paddle
        if newx-Ball.RADIUS < Paddle.WIDTH:
            if abs(newy-paddle_comp.y)<Paddle.HEIGHT//2:
                bounce_effect.play()
                self.vx = -self.vx
                score_comp = score_comp + 1
            #ball doesnt hit computer paddle 
            else:
                while self.x+Ball.RADIUS > 0:
                    self.show(bgColor)
                    self.x = self.x + self.vx
                    self.y = self.y + self.vy
                    self.show(fgColor)
                game_over("Hurray... You WIN!")
                
        #hitting top and bottom borders
        elif newy < BORDER+self.RADIUS or newy > HEIGHT-BORDER-self.RADIUS:
            bounce_effect.play()
            self.vy = -self.vy
            
        #hitting user paddle
        elif newx+Ball.RADIUS > WIDTH-Paddle.WIDTH:
            if abs(newy-paddle_user.y)<Paddle.HEIGHT//2:
                bounce_effect.play()
                self.vx = -self.vx
                score_user = score_user + 1
            #ball doesnt hit user paddle 
            else:
                while self.x-Ball.RADIUS < WIDTH:
                    self.show(bgColor)
                    self.x = self.x + self.vx
                    self.y = self.y + self.vy
                    self.show(fgColor)
                game_over("Oh... AI WINS!")
        #intermediate positions
        else:
            self.show(bgColor)
            self.x = self.x + self.vx
            self.y = self.y + self.vy
            self.show(fgColor)

class Paddle:
    WIDTH = 20
    HEIGHT = 100
    
    def __init__(self, y):
        self.y = y
    
    #Draw user paddle
    def show_user(self, color):
        global screen
        pygame.draw.rect(screen, color, pygame.Rect((WIDTH-self.WIDTH, self.y-self.HEIGHT//2),(self.WIDTH, self.HEIGHT)))
    #Draw computer paddle
    def show_comp(self, color):
        global screen
        pygame.draw.rect(screen, color, pygame.Rect((0, self.y-self.HEIGHT//2),(self.WIDTH, self.HEIGHT)))
        
    #update user paddle position according to mouse position
    def update_user(self):
        newy = pygame.mouse.get_pos()[1]
        global fgColor, bgColor
        if newy-self.HEIGHT//2 > BORDER and newy+self.HEIGHT//2 < HEIGHT-BORDER:
            self.show_user(bgColor)
            self.y = newy
            self.show_user(fgColor)
            
    #update comp paddle position according to data prediction
    def update_comp(self, newy):
        global fgColor, bgColor
        if newy-self.HEIGHT//2 > BORDER and newy+self.HEIGHT//2 < HEIGHT-BORDER:
            self.show_comp(bgColor)
            self.y = newy
            self.show_comp(fgColor)


#create objects

ball = Ball(WIDTH-Ball.RADIUS-Paddle.WIDTH, HEIGHT//2, -VELOCITY, -VELOCITY)
paddle_comp = Paddle(HEIGHT//2)
paddle_user = Paddle(HEIGHT//2)

#Draw the scenario

pygame.init()

clock = pygame.time.Clock()

#screen specifics

screen = pygame.display.set_mode((WIDTH, HEIGHT))
bgColor = pygame.Color("#00203F")
fgColor = pygame.Color("#ADEFD1")
#change default background color
screen.fill(bgColor)

#top and bottom borders
pygame.draw.rect(screen, fgColor, pygame.Rect((0,0),(WIDTH, BORDER)))
pygame.draw.rect(screen, fgColor, pygame.Rect((0,HEIGHT - BORDER),(WIDTH, HEIGHT)))

#Displaying the objects
ball.show(fgColor)
paddle_comp.show_comp(fgColor)
paddle_user.show_user(fgColor)

#loading background music
mixer.music.load('background_music.mp3')
mixer.music.play(-1)


# Scores
score_comp = 0
score_user = 0
gameover = False

#font for displaying score
font = pygame.font.SysFont('monospace', 16)
textX = 2
textY = 2

#display scores on screen
def show_score(x,y):
    pygame.draw.rect(screen, fgColor, pygame.Rect((0,0),(WIDTH, BORDER)))               # to refresh the scoreboard
    score = font.render("AI score: " + str(score_comp) + "    Your score: " + str(score_user), True, bgColor)
    screen.blit(score, (x,y))

#font for displaying gameover
opfont = pygame.font.SysFont('monospace', 48)
gofont = pygame.font.SysFont('freesansbold.ttf', 65)

#gameover updation
def game_over(output_string):
    global gameover
    gameover = True             #pauses the program
    mixer.music.stop()          #stop background music
    mixer.Sound('gameover_effect.wav').play()     #game over sound
    pygame.draw.rect(screen, fgColor, pygame.Rect((100,100),(WIDTH-200, HEIGHT-200)))   #game over screen
    output1 = gofont.render('GAME OVER', True, pygame.Color("black"))
    output2 = opfont.render(output_string, True, bgColor)   #displays who won
    screen.blit(output1, (450,200))
    screen.blit(output2, (400,300))
    
#Using machine learning to train computer
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor

pong = pd.read_csv("game_data.csv")     #file containg data
pong = pong.drop_duplicates()
pong = pong.dropna()
pong = pong.reset_index(drop=True)

X = pong.drop(['paddle_user.y'], axis=1)
Y = pong['paddle_user.y']


clf = KNeighborsRegressor(n_neighbors=3)

clf = clf.fit(X, Y)

df = pd.DataFrame(columns=['x','y','vx','vy'])


while True:
    e = pygame.event.poll()
    if e.type == pygame.QUIT:
        break
    
    clock.tick(200)             #manages speed of program
    
    pygame.display.flip()       #keeps display updated
    
    toPredict = df.append({'x':ball.x, 'y':ball.y, 'vx':ball.vx, 'vy':ball.vy}, ignore_index=True)
    
    prediction = int(clf.predict(toPredict))        #predicts position of y
    
    if not gameover:
        paddle_user.update_user()
        paddle_comp.update_comp(prediction)
        ball.update()
        
    show_score(textX, textY)

pygame.quit()