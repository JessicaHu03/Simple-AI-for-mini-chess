"""CSC111 Winter 2021 Assignment 2: Trees, Chess, and Artificial Intelligence (Part 2)

Instructions (READ THIS FIRST!)
===============================

This Python module contains the start of functions and/or classes you'll define
for Part 2 of this assignment. Please note that in addition to this file, you will
also need to modify a2_game_tree.py by following the instructions on the assignment
handout. You should NOT make any changes to a2_minichess.py.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2021 David Liu and Isaac Waller.
"""
import random
from typing import Optional

import a2_game_tree
import a2_minichess


def generate_complete_game_tree(root_move: str, game_state: a2_minichess.MinichessGame,
                                d: int) -> a2_game_tree.GameTree:
    """Generate a complete game tree of depth d for all valid moves from the current game_state.

    For the returned GameTree:
        - Its root move is root_move.
        - Its `is_white_move` attribute is set using the current game_state.
        - It contains all possible move sequences of length <= d from game_state.
          For each node in the tree, its subtrees appear in the same order that their
          moves were returned by game_state.get_valid_moves(),
        - If d == 0, a size-one GameTree is returned.

    Note that some paths down the tree may have length < d, because they result in an end state
    (win or draw) from game_state in fewer than d moves.

    Preconditions:
        - d >= 0
        - root_move == GAME_START_MOVE or root_move is a valid chess move

    Implementation hints:
        - This function must be implemented recursively.
        - In the recursive step, use the MinichessGame.copy_and_make_move method to create
          a copy of the game state with one new move made.
        - You'll need to review the public interface of the MinichessGame class to see what
          methods are available to help implement this function.

    WARNING: we recommend not calling this function with depth greater than 6, as this will
    likely take a very long time on your computer.
    """
    if d == 0 and root_move == '*':
        game_tree = a2_game_tree.GameTree()

    elif d == 0 and root_move != '*':
        game_tree = a2_game_tree.GameTree(root_move, not game_state.is_white_move())

        gs = game_state.copy_and_make_move(root_move)
        if gs.get_winner() == 'White':
            game_tree.white_win_probability = 1.0

    elif d >= 1 and game_state.get_valid_moves() != [] and root_move == '*':    # Cannot win here
        game_tree = a2_game_tree.GameTree(root_move, game_state.is_white_move())

        subtrees = [a2_game_tree.GameTree(valid_move, not game_state.is_white_move()) for
                    valid_move in game_state.get_valid_moves()]

        for subtree in subtrees:
            subtree = generate_complete_game_tree(subtree.move, game_state, d - 1)
            game_tree.add_subtree(subtree)

    elif d >= 1 and game_state.get_valid_moves() != [] and root_move != '*':
        game_tree = a2_game_tree.GameTree(root_move, not game_state.is_white_move())

        if game_state.get_winner() == 'White':
            game_tree.white_win_probability = 1.0

        gs = game_state.copy_and_make_move(root_move)

        if gs.get_winner() == 'White':
            game_tree.white_win_probability = 1.0

        subtrees = [a2_game_tree.GameTree(valid_move, gs.is_white_move()) for
                    valid_move in gs.get_valid_moves()]

        for subtree in subtrees:
            subtree = generate_complete_game_tree(subtree.move, gs, d - 1)
            game_tree.add_subtree(subtree)

    else:
        game_tree = a2_game_tree.GameTree(root_move, not game_state.is_white_move())

        gs = game_state.copy_and_make_move(root_move)

        if gs.get_winner() == 'White':
            game_tree.white_win_probability = 1.0

    return game_tree


class GreedyTreePlayer(a2_minichess.Player):
    """A Minichess player that plays greedily based on a given GameTree.

    See assignment handout for description of its strategy.
    """
    # Private Instance Attributes:
    #   - _game_tree:
    #       The GameTree that this player uses to make its moves. If None, then this
    #       player just makes random moves.
    _game_tree: Optional[a2_game_tree.GameTree]

    def __init__(self, game_tree: a2_game_tree.GameTree) -> None:
        """Initialize this player.

        Preconditions:
            - game_tree represents a game tree at the initial state (root is '*')
        """
        self._game_tree = game_tree

    def make_move(self, game: a2_minichess.MinichessGame, previous_move: Optional[str]) -> str:
        """Make a move given the current game.

        previous_move is the opponent player's most recent move, or None if no moves
        have been made.

        Preconditions:
            - There is at least one valid move for the given game
        """
        if self._game_tree is not None:

            if previous_move is None:  # Must be white, due to None
                move = helper(self._game_tree.get_subtrees(), True)
                self._game_tree = self._game_tree.find_subtree_by_move(move)
                return move

            elif self._game_tree.get_subtrees() != [] \
                    and previous_move in \
                    {subtree.move for subtree in self._game_tree.get_subtrees()}:
                self._game_tree = self._game_tree.find_subtree_by_move(previous_move)

                if self._game_tree.get_subtrees() != [] and game.is_white_move():
                    move = helper(self._game_tree.get_subtrees(), True)
                    self._game_tree = self._game_tree.find_subtree_by_move(move)
                    return move

                elif self._game_tree.get_subtrees() != [] and not game.is_white_move():
                    move = helper(self._game_tree.get_subtrees(), False)
                    self._game_tree = self._game_tree.find_subtree_by_move(move)
                    return move

            else:
                self._game_tree = None

        return random.choice(game.get_valid_moves())


def helper(lst: list[a2_game_tree.GameTree], find_max: bool) -> str:
    """Pick the leftmost subtree with the max/min white win probability.

    lst is a list of subtrees (at least one) with associated win probabilities.
    if find_max, we find the leftmost max, otherwise the leftmost min.

    """
    temp = lst[0]
    if find_max:
        for item in lst:
            if item.white_win_probability > temp.white_win_probability:
                temp = item
    else:
        for item in lst:
            if item.white_win_probability < temp.white_win_probability:
                temp = item

    return temp.move


def part2_runner(d: int, n: int, white_greedy: bool) -> None:
    """Create a complete game tree with the given depth, and run n games where
    one player is a GreedyTreePlayer and the other is a RandomPlayer.

    The GreedyTreePlayer uses the complete game tree with the given depth.
    If white_greedy is True, the White player is the GreedyTreePlayer and Black is a RandomPlayer.
    This is switched when white_greedy is False.

    Preconditions:
        - d >= 0
        - n >= 1

    Implementation notes:
        - Your implementation MUST correctly call a2_minichess.run_games. You may choose
          the values for the optional arguments passed to the function.
    """
    game_tree = generate_complete_game_tree('*', a2_minichess.MinichessGame(), d)

    if white_greedy:
        white_player = GreedyTreePlayer(game_tree)
        black_player = a2_minichess.RandomPlayer()
    else:
        white_player = a2_minichess.RandomPlayer()
        black_player = GreedyTreePlayer(game_tree)

    a2_minichess.run_games(n, white_player, black_player, show_stats=True)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 100,
        'max-nested-blocks': 4,
        'disable': ['E1136'],
        'extra-imports': ['random', 'a2_minichess', 'a2_game_tree']
    })

    # Sample call to part2_runner (you can change this, just keep it in the main block!)
    # part2_runner(5, 50, False)
