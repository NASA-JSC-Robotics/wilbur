#!/usr/bin/env python3
RESET_COLOR = "\033[0m"
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"  # orange on some systems
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
LIGHT_GRAY = "\033[37m"
DARK_GRAY = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
WHITE = "\033[97m"


def pig_mockhardware(separate_controls_pcs_bool=False):
    if separate_controls_pcs_bool:
        print(
            BLUE
            + r"""
          .-.___.-.     _.---------._
         /         \ *`               `\    6.
        |  0      0 |      Wilbur       \    9
        |  ( ○  ○ ) |  in mock hardware  |  /
         '-_______.-     - separate -     |/
                 |       control PCs     |
                 *             ___       *
                  \    / \    /   \ \   /
                   *__*   *__*     *_*_*"""
            + RESET_COLOR
        )

    else:
        print(
            CYAN
            + r"""
          .-.___.-.     _.---------._
         /         \ *`               `\    6.
        |  0      0 |      Wilbur       \    9
        |  ( ○  ○ ) |  in mock hardware  |  /
         '-_______.-      -  one  -      |/
                |       control PC      |
                *             ___       *
                 \    / \    /   \ \   /
                  *__*   *__*     *_*_*"""
            + RESET_COLOR
        )


def pig_hardware(separate_controls_pcs_bool=False):
    if separate_controls_pcs_bool:
        print(
            BRIGHT_MAGENTA
            + r"""
          .-.___.-.     _.---------._
         /         \ *`               `\    6.
        |  0      0 |      Wilbur       \    9
        |  ( ○  ○ ) |     Hardware        |  /
         '-_______.-     - separate -     |/
                 |       control PCs     |
                 *             ___       *
                  \    / \    /   \ \   /
                   *__*   *__*     *_*_*"""
            + RESET_COLOR
        )
    else:
        print(
            BRIGHT_GREEN
            + r"""
          .-.___.-.     _.---------._
         /         \ *`               `\    6.
        |  0      0 |      Wilbur       \    9
        |  ( ○  ○ ) |     Hardware       |  /
         '-_______.-      -  one  -      |/
                |       control PC      |
                *             ___       *
                 \    / \    /   \ \   /
                  *__*   *__*     *_*_*"""
            + RESET_COLOR
        )


def pig_gazebo():
    print(
        YELLOW
        + r"""
          .-.___.-.     _.---------._
         /         \ *`               `\    6.
        |  0      0 |      Wilbur       \    9
        |  ( ○  ○ ) |      Gazebo         |  /
         '-_______.-                      |/
                 |                       |
                 *             ___       *
                  \    / \    /   \ \   /
                   *__*   *__*     *_*_*"""
        + RESET_COLOR
    )
