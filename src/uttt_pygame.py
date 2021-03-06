from uttt_data import *
from pygame_game import PygameGame
import pygame, pygame.locals
import uttt_data
from pygame import *
import pygame, sys
import time

class UTTTGame(PygameGame):



    def __init__(self, width_px, height_px, frames_per_second, data, send_queue):
        # PygameGame sets self.width and self.height        
        PygameGame.__init__(self, "Ultimate Tic Tac Toe", width_px, height_px, frames_per_second)
        pygame.font.init()
        self.data = data
        self.send_queue = send_queue
        self.font = pygame.font.SysFont("leelawadee",14)
        self.gfont = pygame.font.SysFont("Lithos Pro", 25)
        self.image = pygame.image.load("dude_surfin.png")
        self.gameover = pygame.image.load("beach-over.png")
        self.player1 = pygame.image.load("pearl_dribbble.png")
        self.player2 = pygame.image.load("starfishicon.png")
        pygame.mixer.init()
        self.music = pygame.mixer.music.load("Wallpaper.mp3")

        pygame.mixer.music.play(-1, 0.0)

        self.drawRect = 1
        self.transCount = 0
        self.transIncrement = 25
        self.gameOver= False
        return

    def handle_state(self):
        if self.data:
            state = self.data.GetState()
            if state in [ uttt_data.STATE_SHOW_SIGNUP, uttt_data.STATE_WAIT_SIGNUP, 
                          uttt_data.STATE_SIGNUP_FAIL_USERNAME,
                          uttt_data.STATE_SHOW_LOGIN, uttt_data.STATE_WAIT_LOGIN, uttt_data.STATE_LOGIN_FAIL,
                          uttt_data.STATE_SIGNUP_FAIL_EMAIL, uttt_data.STATE_SIGNUP_FAIL_PASSWORD,
                          uttt_data.STATE_SIGNUP_FAIL_PASSWORD_UNMATCHED, uttt_data.STATE_SIGNUP_OK ]:
                # minimize window
                #pygame.display.iconify()
                if self.screen.get_size() != ( 1, 1 ):
                    print "shrink"
                    self.screen = pygame.display.set_mode(
                        # set the size
                        (1, 1),
                        # use double-buffering for smooth animation
                        pygame.DOUBLEBUF |
                        # apply alpha blending
                        pygame.SRCALPHA |
                        # allow resizing
                        pygame.RESIZABLE)
                
            elif state in [ uttt_data.STATE_WAIT_GAME, uttt_data.STATE_SHOW_GAME,
                            uttt_data.STATE_GAME_OVER, uttt_data.STATE_TURN_FAILED,
                            uttt_data.STATE_WAIT_TURN ]:
                # unminimize window
                if self.screen.get_size() != ( self.width, self.height ):
                    print "WHAT?  pygame doesn't support unminimize?"
                    self.screen = pygame.display.set_mode(
                        # set the size
                        (self.width, self.height),
                        # use double-buffering for smooth animation
                        pygame.DOUBLEBUF |
                        # apply alpha blending
                        pygame.SRCALPHA |
                        # allow resizing
                        pygame.RESIZABLE)
            elif state in [ uttt_data.STATE_SOCKET_CLOSED, uttt_data.STATE_SOCKET_ERROR,
                            uttt_data.STATE_ERROR ]:
                # close
                print "Socket closed, or other error, pygame will quit."
                time.sleep(2)
                self.gameOver = True
            elif state in [ uttt_data.STATE_SOCKET_OPEN ]:
                # what should I do?
                pass
            else:
                print "Unknown state in pygame: ", state

        return

    def game_logic(self, keys, newkeys, buttons, newbuttons, mouse_position):
        self.handle_state()
        
        if 1 in newbuttons:
            if self.data.GetNextPlayer() != self.data.GetPlayer():
                # not our turn
                return

            mX,mY = mouse_position[0], mouse_position[1]
            col = mX / (self.width/9)
            row = mY / (self.height/9)
            board = 3 * (row / 3) + (col / 3)
            position = 3 * (row % 3) + (col % 3)

            if board == self.data.GetNextBoard() or self.data.GetNextBoard() == -1:
                if self.data.GetBoardOwner(board) == "N":
            
                    if self.data and self.send_queue:
                        text = self.data.SendTurn(board, position)
                        print "pygame: queuing: %s" % (text, )
                        self.send_queue.put(text)
                    
        if pygame.K_i in newkeys:
            
            print("detected")
            self.drawRect *= -1
            #self.transCount = 0
            
        return

    def paint(self, surface):
        if self.gameOver == False:
            # Background
            rect = pygame.Rect(0,0,self.width,self.height)
            # surface.fill((200,255,0, 0.5),rect )
            surface.blit(self.image, (0,0))

            
            #Board Marker
            if self.data.GetNextBoard() != -1 and self.data.GetNextPlayer() == self.data.GetPlayer():
                x = (self.data.GetNextBoard() % 3) * (self.width/3)
                y = (self.data.GetNextBoard() / 3) * (self.height/3)
                #print(x,y)
                rect = pygame.Rect(x,y,self.width/3,self.height/3)
                self.drawTransparentRect(surface, (255, 255, 255, 100), rect)
            #Board Owner Marker
            for i in range(0,8):
                if self.data.GetBoardOwner(i) == "X":
                    x = (i % 3) * (self.width/3)
                    y = (i / 3) * (self.height/3)
                    rect = pygame.Rect(x,y,self.width/3,self.height/3)
                    self.drawTransparentRect(surface, (100, 0, 0, 100), rect)

                elif self.data.GetBoardOwner(i) == "O":
                    x = (i % 3) * (self.width/3)
                    y = (i / 3) * (self.height/3)
                    rect = pygame.Rect(x,y,self.width/3,self.height/3)
                    self.drawTransparentRect(surface, (0, 0, 100, 100), rect)
  

            
            # Regular Lines
            for i in range(1,9):
                pygame.draw.line(surface, (255,255,255), (0, i*self.height/9), (self.width, i*self.height/9))
            for j in range(1,9):
                pygame.draw.line(surface, (255,255,255), (j*self.width/9, 0), (j*self.height/9, self.height))

            # Board Lines
            for k in range(1,3):
                pygame.draw.line(surface, (0,0,0), (0, k*self.height/3), (self.width, k*self.height/3), 3)
            for l in range(1,3):
                pygame.draw.line(surface, (0,0,0), (l*self.width/3, 0), (l*self.height/3, self.height), 3)

            # Markers
            for board in range(9):
                for position in range(9):
                    col = 3 * (board % 3) + position % 3
                    row = 3 * (board / 3) + position / 3
                    x = int((col + .5) * self.width / 9)
                    y = int((row + .5) * self.height / 9)
                    marker = self.data.GetMarker(board, position)
                    if marker == uttt_data.PLAYER_X:
                        surface.blit(self.player1, (x-25,y-25))
                    elif marker == uttt_data.PLAYER_O:
                        surface.blit(self.player2, (x-25,y-25))
            #This needs to happen when I hit 'i':
            if self.drawRect == 1:
                #Text Rect
                rect = pygame.Rect(0, 533, 200, 66)
                self.drawTransparentRect(surface, (255, 255, 255, self.transCount), rect)
                if self.transCount < 100:
                    self.transCount += self.transIncrement
            else:
                rect = pygame.Rect(0, 533, 200, 66)
                self.drawTransparentRect(surface, (255, 255, 255, self.transCount), rect)
                if self.transCount > 0:
                    self.transCount -= self.transIncrement
                    if self.transCount < 0:
                        self.transCount = 0
            if self.transCount > 0:
                #Text
                pName = self.data.GetPlayerName()
                self.drawTextLeft(surface, pName, (0, 0, 100), 5, 555, self.font)
                oName = self.data.GetOpponentName()
                self.drawTextLeft(surface, oName, (100, 0, 0), 5, 570, self.font)
                cPlayer = self.data.GetNextPlayer()
                if self.data.GetState() == 8:
                    if cPlayer == self.data.GetPlayer():
                        cPlayer = ("Your turn")
                    else:
                        cPlayer = ("Their turn")
                else:
                    cPlayer = ("Waiting for opponent...")
                self.drawTextLeft(surface, cPlayer, (0, 0, 0), 5, 585, self.font)
                self.drawTextLeft(surface, "i to toggle stats", (0, 0, 0), 5, 600, self.font)
        else:
            # Game Over Screen
            rect = pygame.Rect(0,0,self.width,self.height)
            surface.blit(self.gameover, (0,0))
            if self.data.GetWinner() == self.data.GetPlayer():
                self.drawTextLeft(surface, self.data.GetPlayerName(), (244, 133, 75), 350, 400, self.gfont)
            else:
                self.drawTextLeft(surface, self.data.GetOpponentName(), (244, 133, 75), 350, 395, self.gfont)


        return
        
    def drawTextLeft(self, surface, text, color, x, y, font):
        textobj = font.render(text, False, color)
        textrect = textobj.get_rect()
        textrect.bottomleft = (x, y)
        surface.blit(textobj, textrect)
        return
    def drawTransparentRect(self, surface, color, rect):
        rect_surface = pygame.Surface( (rect.width, rect.height), pygame.locals.SRCALPHA )
        rect_surface.fill( (0,0,0,0) )
        r = pygame.Rect(0, 0, rect.width, rect.height)
        pygame.draw.rect(rect_surface, color, r)
        surface.blit(rect_surface, (rect.left, rect.top))
        return

    
def uttt_pygame_main(data, send_queue):
    game = UTTTGame(600, 600, 30, data, send_queue)
    game.main_loop()
    return

if __name__ == "__main__":
    uttt_pygame_main(UTTTData(), None)
