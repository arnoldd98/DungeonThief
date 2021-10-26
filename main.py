from kivy.config import Config
Config.set('graphics', 'resizable', False)  # fix window size

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.core.audio import SoundLoader

from libdw import sm
from math import sqrt
import copy
import random


# Dragon state machine
class Dragon(sm.SM):
    # Dragon has 6 states: 0-5, in increasing order of likelihood of waking up
    start_state = 0

    # dist_lst contains critical distances between player and dragons, starting from furthest
    # vol_lst contains critical volume levels, starting from softest
    def __init__(self, dist_lst, vol_lst):
        self.dist = dist_lst
        self.vol = vol_lst

    # check state every time player changes his position
    # input is a tuple, which consist of  1. current distance between the dragon and the player
    # 2. volume of the player's footsteps
    def get_next_values(self, state, inp):
        out = None
        d = inp[0]
        v = inp[1]
        if d > self.dist[0]:
            if v <= self.vol[1]:
                state -= 1 if state != 0 else 0
            elif self.vol[1] < v:
                if state > 1:
                    state -= 1 if state != 1 else 1
                elif state == 0:
                    state = 1

        elif self.dist[1] < d <= self.dist[0]:
            if v <= self.vol[1]:
                state -= 1 if state != 0 else 0
            elif self.vol[1] < v <= self.vol[2]:
                if state == 0:
                    state = 1
            elif self.vol[2] < v <= self.vol[3]:
                if state == 0 or state == 2 or state == 3:
                    if random.random() < 0.5:
                        state += 1

        elif self.dist[2] < d <= self.dist[1]:
            if v <= self.vol[0]:
                if state == 4:
                    state = 3
            if self.vol[0] < v <= self.vol[1]:
                if state == 0 or state == 1:
                    if random.random() < 0.5:
                        state += 1
            if self.vol[1] < v <= self.vol[2]:
                if state == 0 or state == 1 or state == 2:
                    if random.random() < 0.5:
                        state += 1
            if self.vol[2] < v <= self.vol[3]:
                if random.random() < 0.5:
                    state += 1 if state < 5 else 5

        elif d <= self.dist[2]:
            if v <= self.vol[0]:
                if state == 0 or state == 1:
                    if random.random() < 0.5:
                        state += 1
            if self.vol[0] < v <= self.vol[1]:
                if random.random() < 0.5:
                    if state < 5:
                        state += 1
            if self.vol[1] < v <= self.vol[2]:
                if state == 0 or state == 1 or state == 2:
                    if random.random() < 0.5:
                        state += 1
                elif state == 3 or state == 4:
                    state += 1
            if self.vol[2] < v <= self.vol[3]:
                if state == 0 or state == 1:
                    if random.random() < 0.5:
                        state += 2
                    else:
                        state += 1
                elif state == 2 or state == 3:
                    if random.random() < 0.5:
                        state += 1
                elif state == 4:
                    if random.random() < 0.5:
                        state = 5

        if state == 0 and v >= self.vol[2]:      # above a certain volume, state never goes back to 0
            state == 1

        return state, out


# The game 'engine'
class DungeonGame:
    def __init__(self, grid, critical_dist, dragon_pos, exit_pos, number_of_gold):
        # format of grid should be:
        # [[0,0], [0,y], [0,2y], ...
        #   [x,0], [x,y], [x,2y], ...
        #   [2x,0], [2x,y], [2x, 2y], ...], where x and y are increments

        self.score = 0  # score counter
        self.volume = 0.1  # sound of footsteps
        grid = [i for i in grid if i not in dragon_pos]  # remove position of dragon from grid
        self.grid = grid  # list of possible positions occupied by player or gold
        self.dragon = Dragon(critical_dist, [0.2, 0.4, 0.7, 1.0])  # enter the dragon and add critical volumes
        self.dragon.start()

        self.dragon_pos = dragon_pos  # set position of dragon
        self.exit_pos = exit_pos  # set position of exit
        self.player_pos = copy.deepcopy(exit_pos)  # set initial position of player
        self.endGame = False  # check if game ends
        self.number_of_gold = number_of_gold
        self.gold_pos = self.setGoldPos(number_of_gold)  # set position of gold

    # place n amount of gold on random positions
    def setGoldPos(self, number_of_gold):  # called during initialization
        gold_pos = []
        for i in range(number_of_gold):
            index = random.randint(0, len(self.grid) - 1)
            gold_pos.append((self.grid[index]))

        return gold_pos

    # calls when player moves in any direction
    # checks for any events
    def move(self, direction):
        x_incr = 0
        y_incr = self.grid[1][1] - self.grid[0][1]
        for i in range(0, len(self.grid)):
            if self.grid[i][0] < self.grid[i + 1][0]:
                x_incr = self.grid[i + 1][0] - self.grid[i][0]
                break

        if direction == "up":
            self.player_pos[1] += y_incr
            if self.player_pos not in self.grid:
                self.player_pos[1] -= y_incr
                print("Out of bounds!")

        if direction == "down":
            self.player_pos[1] -= y_incr
            if self.player_pos not in self.grid:
                self.player_pos[1] += y_incr
                print("Out of bounds!")

        if direction == "right":
            self.player_pos[0] += x_incr
            if self.player_pos not in self.grid:
                self.player_pos[0] -= x_incr
                print("Out of bounds!")

        if direction == "left":
            self.player_pos[0] -= x_incr
            if self.player_pos not in self.grid:
                self.player_pos[0] += x_incr
                print("Out of bounds!")

        # check if player exits
        if self.player_pos == self.exit_pos:
            self.endGame = True

        # check if the dragon awakes
        dist = sqrt((self.dragon_pos[4][0] - self.player_pos[0]) ** 2 +
                    (self.dragon_pos[4][1] - self.player_pos[1]) ** 2)

        self.dragon.step((dist, self.volume))
        if self.dragon_wakes():
            self.score = 0
            self.endGame = True

        # check if player collected gold
        if self.player_pos in self.gold_pos:
            self.score += 10
            self.volume += (0.9 / self.number_of_gold)
            self.gold_pos.remove(self.player_pos)
            return self.player_pos

        return None

    # check if game is lost (aka dragon wakes up) by calculating probability from dragon's state
    def dragon_wakes(self):
        probability = 0
        if self.dragon.state == 0:
            probability = 0.001
        elif self.dragon.state == 1:
            probability = 0.005
        elif self.dragon.state == 2:
            probability = 0.01
        elif self.dragon.state == 3:
            probability = 0.025
        elif self.dragon.state == 4:
            probability = 0.05
        elif self.dragon.state == 5:
            probability = 0.2

        print("Probability of getting caught: ", probability)
        if random.random() < probability:
            return True
        else:
            return False

    # restarts game and restores everything to their original settings
    def restart_game(self):
        self.player_pos = copy.deepcopy(self.exit_pos)
        self.gold_pos = self.setGoldPos(self.number_of_gold)
        self.score = 0
        self.volume = 0.1
        self.dragon.state = 0
        self.endGame = False


# UI Component of Game
class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_key_down)

        # load top menu bar
        self.size = (780, 580)
        self.scorelabel = Label(text="Score: 0", font_size=20, pos=(0, 535))
        self.add_widget(self.scorelabel)
        self.restartbutton = Button(on_press=self.restartGame, text="Restart", size=(100, 40), pos=(700, 570), )
        self.add_widget(self.restartbutton)

        # set game parameters
        box_len = self.size[0] / 40
        self.box_len = box_len
        grid = []
        exit_pos = []
        dragon_pos = []
        for a in range(41):
            for b in range(int(self.size[1] // box_len)):
                x = a * box_len
                y = b * box_len
                grid.append([x, y])
                if x == 20 * box_len and y == 0:
                    exit_pos = [x, y]
                if 18 * box_len <= x <= 22 * box_len <= y <= 26 * box_len:
                    dragon_pos.append([x,y])
        critical_dist = [320, 250, 180]
        self.game = DungeonGame(grid, critical_dist, dragon_pos, exit_pos, 30)

        # load sound of footsteps
        self.footstep1 = SoundLoader.load('Sounds/Footstep1.wav')
        self.footstep2 = SoundLoader.load('Sounds/Footstep2.wav')
        self.footstep3 = SoundLoader.load('Sounds/Footstep3.wav')
        self.footstep_lst = [self.footstep1, self.footstep2, self.footstep3]
        for footstep in self.footstep_lst:
            footstep.volume = self.game.volume

        # 'draw' the game out on the window
        with self.canvas:
            # 'draw' marker to show how close dragon is to waking
            self.meter_bar = Rectangle(pos=(200, 590), size=(50, box_len))

            # 'draw' gold on the canvas
            self.gold_lst = []
            for pos in self.game.gold_pos:
                goldpic = 'Images/gold.png' if random.random() < 0.5 else 'Images/gold2.png'
                self.gold_lst.append(Rectangle(pos=pos, size=(box_len, box_len), source=goldpic))

            # 'draw' dragon, exit and player
            Rectangle(pos=dragon_pos[0], size=(box_len * 5, box_len * 5), source='Images/dragon.png')
            Rectangle(pos=exit_pos, size=(box_len, box_len), source='Images/exit.png')
            self.player = Rectangle(pos=self.game.player_pos, size=(box_len, box_len), source='Images/robber.png')

            Color(1, 1, 1, 1)
        self.no_of_steps = 0

    def _on_keyboard_closed(self):
        if self._keyboard is not None:
            self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.no_of_steps += 1

        i = random.randint(0, 2)
        self.footstep_lst[i].play()
        if text == "w":
            self.game.move("up")
            self.player.pos = self.game.player_pos
        elif text == "a":
            self.game.move("left")
            self.player.pos = self.game.player_pos
        elif text == "d":
            self.game.move("right")
            self.player.pos = self.game.player_pos
        elif text == "s":
            self.game.move("down")
            self.player.pos = self.game.player_pos

        # adjust size of meter bar based on dragon state
        if self.game.dragon.state == 0:
            self.meter_bar.size = (80, self.box_len)
        elif self.game.dragon.state == 1:
            self.meter_bar.size = (160, self.box_len)
        elif self.game.dragon.state == 2:
            self.meter_bar.size = (240, self.box_len)
        elif self.game.dragon.state == 3:
            self.meter_bar.size = (320, self.box_len)
        elif self.game.dragon.state == 4:
            self.meter_bar.size = (400, self.box_len)
        elif self.game.dragon.state == 35:
            self.meter_bar.size = (480, self.box_len)

        # remove gold from canvas after collection
        for gold in self.gold_lst:
            if self.player.pos == gold.pos:
                for footstep in self.footstep_lst:
                    footstep.volume = self.game.volume
                self.gold_lst.remove(gold)
                self.canvas.remove(gold)

        # if game ends due to player exiting or getting caught by dragon
        if self.game.endGame:
            print("Game ends! Total number of steps taken: ", self.no_of_steps)
            self._on_keyboard_closed()
            if self.game.dragon.state == 3:
                final_score = "You been caught! Final Score: 0"
            else:
                final_score = "End game! Your score: " + str(self.game.score)
            restartbutton = Button(text=final_score, on_press=self.restartGame)

            self.endpopup = Popup(content=restartbutton, title="",
                                  auto_dismiss=False, size_hint=(None, None), size=(400, 200))
            self.endpopup.open()

        # edit score label
        score = "Score:" + str(self.game.score)
        self.scorelabel.text = score

    # restarts the game and returns everything to their original position
    # also starts up the keyboard since keyboard input should be disabled after pop-up appears
    def restartGame(self, instance):
        try:
            self.endpopup.dismiss()
        except:
            self.endpopup = Popup()

        self.game.restart_game()
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_key_down)
        self.meter_bar.size = (80, self.box_len)

        for footstep in self.footstep_lst:
            footstep.volume = self.game.volume

        for remaining_gold in self.gold_lst:
            self.canvas.remove(remaining_gold)

        self.gold_lst = []
        for pos in self.game.gold_pos:
            goldpic = 'Images/gold.png' if random.random() < 0.5 else 'Images/gold2.png'
            gold = Rectangle(pos=pos, size=(self.box_len, self.box_len), source=goldpic)
            self.gold_lst.append(gold)
            self.canvas.add(gold)

        self.scorelabel.text = "Score: 0"
        self.player.pos = self.game.player_pos


class GameApp(App):
    def build(self):
        return GameWidget()


if __name__ == '__main__':
    app = GameApp()
    app.run()
