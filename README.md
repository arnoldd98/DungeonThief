DONE for 10.009 Digital World FInal Assignment.
Also my first python project :)

Gameplay video link: https://youtu.be/2qpPOTd5xoA

# Sypnosis
Ghabi's Greed features a robber venturing into a dragon's lair in his 
search for riches. He has one set objective - to collect as many gold
as he can from the dragon's stash while it sleeps. With every step he 
takes, the robber faces the risk of awakening the dragon and facing its
wrath. Can he make it out safely to a life of riches, or be caught 
red-handed and face retribution for his greed?

# Gameplay
The player starts out at the entrance at the bottom of the screen. The
only controls are WASD to move. The gold pieces are placed randomly
around the map. Every time the player collects a piece of gold, 10 is 
added to the score counter; however the volume of his footsteps also 
increases. For every step the player takes, there is a chance of the 
dragon waking up and the player loses the game with a score of 0. This 
is reflected by the white bar at the top of the screen. The longer the 
bar, the more likely the player gets caught. The length of the bar 
depends on two factors: the volume of the player's footsteps and the 
distance between the player and the dragon.

To exit the map and end the game, the player has to go to where he
came from - the entrance at the bottom of the screen. After the game ends,
a pop-up comes out which shows the final score of the player. Clicking on
the pop-up would start a new game, with all the gold pieces rearranged.
The player can also choose to restart the game anytime by clicking the
button at the top right of the screen - however by doing so, the score
counter resets and the player is returned to where he came from.

# Code
The dragon is a state machine with a range of states from 0 to 5 that 
takes in the volume of the player's footsteps and the distance between 
the player and the dragon as inputs. In the game code, the state of the 
dragon is translated to the probability the dragon wakes up. The higher 
the state, the more likely it is to wake up. Naturally, the louder the 
volume or the closer the player is, the higher the state of the dragon.
To add to the randomness of the game, the dragon's state always have a 
50% chance to increase at critical distances and volumes rather than
100%. This adds to the strategy where the player has to tread carefully,
and retreat when the state elevates.

The core game mechanics and interface are separated into two different
classes, to allow for code to be more organised and sources for issues to
be pinpointed more easily. The DungeonGame class is responsible for
creating the 'game board' for the game and controlling events when the 
player moves, such as the collection of gold or checking whether the 
dragon wakes up. An instance of the dragon state machine is created in 
the class, which then 'translate' its state to probability in the 
dragon_wakes function. The DungeonGame class is made in such a way that
it can work with any other GUI classes, as it creates the game based on
a given list of coordinates.

The GameWidget class is a subclass of the Widget class from Kivy. An 
instance of the DungeonGame class is called in here. Its main purpose is
to create a GUI based on the game. While the DungeonGame instance sees 
the game as a grid of fixed coordinates, the GameWidget applies the grid
coordinates to a canvas, where image assets would represent key
components such as the dragon, player and gold pieces. The GameWidget
also covers up the limitations of the DungeonGame class, such as
determining the critical distances where the dragon could change state,
since the DungeonGame class cannot easily determine these distances 
as they vary for different interface sizes. 

