#!/usr/bin/env python

def pig_mockhardware(separate_controls_pcs_bool):
    if separate_controls_pcs_bool:
        color = '\033[94m'
        print(color + 
        """
          .-.___.-.     _.---------._
         /         \ *`               `\    6.
        |  0      0 |      Wilbur       \    9
        |  ( ○  ○ ) |  in mock hardware  |  /
         '-_______.-     - separate -     |/
                 |       control PCs     |
                 *             ___       *
                  \    / \    /   \ \   /
                   *__*   *__*     *_*_*""")
    else:
        color = '\033[94m'
        print(color + 
        """ 
          .-.___.-.     _.---------._
         /         \ *`               `\    6.
        |  0      0 |      Wilbur       \    9
        |  ( ○  ○ ) |  in mock hardware  |  /
         '-_______.-      -  one  -      |/
                |       control PC      |
                *             ___       *
                 \    / \    /   \ \   /
                  *__*   *__*     *_*_*""")

def pig_hardware(separate_controls_pcs_bool):
    if separate_controls_pcs_bool:
        color = '\033[94m'
        print(color + 
        """
          .-.___.-.     _.---------._
         /         \ *`               `\    6.
        |  0      0 |      Wilbur       \    9
        |  ( ○  ○ ) |     Hardware        |  /
         '-_______.-     - separate -     |/
                 |       control PCs     |
                 *             ___       *
                  \    / \    /   \ \   /
                   *__*   *__*     *_*_*""")
    else:
        color = '\033[94m'
        print(color + 
        """ 
          .-.___.-.     _.---------._
         /         \ *`               `\    6.
        |  0      0 |      Wilbur       \    9
        |  ( ○  ○ ) |     Hardware       |  /
         '-_______.-      -  one  -      |/
                |       control PC      |
                *             ___       *
                 \    / \    /   \ \   /
                  *__*   *__*     *_*_*""")
        
def pig_gazebo():
        color = '\033[94m'
        print(color + 
        """
          .-.___.-.     _.---------._
         /         \ *`               `\    6.
        |  0      0 |      Wilbur       \    9
        |  ( ○  ○ ) |      Gazebo         |  /
         '-_______.-                      |/
                 |                       |
                 *             ___       *
                  \    / \    /   \ \   /
                   *__*   *__*     *_*_*""")