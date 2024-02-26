[中文版](README.md)

# [14mv_draft] Introduction

This program is an out-of-the-box drafting software specially developed for "14 Minesweeper Variants Demo" (abbreviated as 14mv), customized for Xiaowen @initrel-0xardye. It aims to provide rich drafting features and better support for classification discussions. With 14mv_draft, you can say goodbye to traditional pen and paper and tackle Minesweeper challenges with ease (at least that's our hope).

# Interface Introduction and How to Use

1. **Import Puzzle Screenshot**: Use the import function from the file menu to import a screenshot of the Minesweeper puzzle. 14mv_draft will automatically detect the puzzle size, draw it on the screen, and create an initial branch.
2. **Interface Layout**: The interface of 14mv_draft is divided into three parts: the branch list on the left, the drafting board in the middle, and the function menu on the right.
3. **Drafting and Classification Discussion**: In the center of the drafting area, you can mark mines and non-mines and create branches for classification discussions.
4. **Automatic Solution Detection**: After the discussion, 14mv_draft will automatically detect if there are cells that have the same solution in all branches. If so, they will be marked with a yellow square, indicating that the corresponding cell has been solved.

# Main Features and Shortcuts

- **Classification Discussion**: Middle-click the corresponding location to automatically create two branches, discussing whether the current cell is a mine.
- **Check All Classifications with One Key (check branch)**: Press the spacebar to check if any cells have a unique solution in all classifications.
- **Mark Mines and Non-mines**: Left-click to mark non-mines, right-click to mark mines, click again to cancel.
- **Toggle Drawing Mode (toggle drawing)**: Press `D` to switch between drawing mode and Minesweeper mode, with preset or custom paint colors available in the right color area. Left-click to draw, right-click for eraser.
- **Clear Drawing Marks**: Press `X` to clear the current branch's drawing marks.
- **Copy Current Branch (copy branch)**: Press `C` to copy the current branch.
- **Delete Current Branch (delete branch)**: Press `Delete` to delete the current branch.
- **Mark Branch Completion Status**: Press `Enter` to mark the current branch's completion status, press again to unmark. Used to record discussed branches (completed/uncompleted).
- **Reset Branch Status (reset status)**: Press `N` to reset all branches to the unprocessed status.
- **Quick Branch Switching**: Use the up and down arrow keys to quickly switch branches.

These shortcuts allow you to perform related actions through the keyboard while the application is focused, enhancing the smoothness of the workflow and the speed of accessing functions.

# Installation Instructions

- Requires Python version >=3.6 (developed with 3.7.13).
- Clone the repository: `git clone https://github.com/Thecats-Jfm/14mv_draft.git`
- Install dependencies: `pip install -e .`

# Starting the Program

Run `14mvd` from the command line to start the program.

# Notes

- The current version supports color schemes including preset 1 and pink-white. See `img/pink_white.png` and `img/set1.png` for details.

# Interface Screenshot Example
![Interface Screenshot Example](img/exp.png)

*Love my wife*
