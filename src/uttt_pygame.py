from uttt_data import *
from pygame_game import PygameGame
import pygame, pygame.locals
import uttt_data
from pygame import *
import pygame, sys

class UTTTGame(PygameGame):

    def __init__(self, width_px, height_px, frames_per_second, data, send_queue):
        # PygameGame sets self.width and self.height        
        PygameGame.__init__(self, "Ultimate Tic Tac Toe", width_px, height_px, frames_per_second)
        pygame.font.init()
        self.data = data
        self.send_queue = send_queue
        self.font = pygame.font.SysFont("San Serif",14)
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
                pygame.quit()
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
            
            if self.data and self.send_queue:
                text = self.data.SendTurn(board, position)
                print "pygame: queuing: %s" % (text, )
                self.send_queue.put(text)
        return

    def paint(self, surface):
        # Background
        # rect = pygame.Rect(0,0,self.width,self.height)
        # surface.fill((200,255,0),rect )
        background_file_name = "dude_surfin.png"
        background_surface = pygame.image.load(background_file_name)
        screen.blit(background_surface, (0,0))

        
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
                    pygame.draw.circle(surface, (0,0,255), (x, y), 5)
                elif marker == uttt_data.PLAYER_O:
                    pygame.draw.circle(surface, (255,0,0), (x, y), 5)
        #Text
        pName = self.data.GetPlayerName()
        self.drawTextLeft(surface, pName, (0, 0, 255), 10, 30, self.font)
        oName = self.data.GetOpponentName()
        self.drawTextLeft(surface, oName, (255, 0, 0), 10, 50, self.font)
        cPlayer = self.data.GetNextPlayer()
        if self.data.GetState() == 8:
            if cPlayer == self.data.GetPlayer():
                cPlayer = ("Your turn")
            else:
                cPlayer = ("Their turn")
        else:
            cPlayer = ("Patience is a Virtue, It's your opponents turn...")
        self.drawTextLeft(surface, cPlayer, (255, 0, 0), 10, 90, self.font)
        #Board
        if self.data.GetState() == 8:
            nBoard = self.data.GetNextBoard()
            nBoard = "Board #" + str(nBoard)
            self.drawTextLeft(surface, str(nBoard), (0, 0, 0), 10, 70, self.font)
        return
    
    def drawTextLeft(self, surface, text, color, x, y, font):
        textobj = font.render(text, False, color)
        textrect = textobj.get_rect()
        textrect.bottomleft = (x, y)
        surface.blit(textobj, textrect)
        return

def uttt_pygame_main(data, send_queue):
    game = UTTTGame(600, 600, 30, data, send_queue)
    game.main_loop()
    return

if __name__ == "__main__":
    uttt_pygame_main(UTTTData(), None)
