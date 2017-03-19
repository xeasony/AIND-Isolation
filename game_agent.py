"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random

no_move = (-1, -1)

directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2),  (1, 2), (2, -1),  (2, 1)]

class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    option = 2

    own_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(game.get_opponent(player))

    len_own_moves = len(own_moves)
    len_opp_moves = len(opp_moves)

    if option == 1:
        return float(len_own_moves - 3 * len_opp_moves)
    else:
        blank_positions = game.get_blank_spaces()

        next_x, next_y = -1, -1

        len_next_own_moves = 0
        len_second_next_own_moves = 0

        # Try to go deeper one level and select two position which potentially have
        # the greatest number of moves.
        for (x, y) in own_moves:
            count = 0
            for (xi, yi) in directions:
                if (x + xi, y + yi) in blank_positions:
                    count += 1

            if count >= len_next_own_moves:
                next_x = x
                next_y = y
                len_second_next_own_moves = len_next_own_moves
                len_next_own_moves = count
            elif count > len_second_next_own_moves:
                len_second_next_own_moves = count

        # if best next move is in opponent's moves
        # then opponent can take it --> we should avoid this option
        if (next_x, next_y) in opp_moves:
            k1 = 0

        if option == 2:
            # The heuristic will finally be the sum of available moves of two next best move
            # minus 2 * number of opponent's moves
            return float(len_own_moves + 2 * len_next_own_moves - 3 * len_opp_moves)
        else:
            return float(3 * len_next_own_moves + len_second_next_own_moves - 3 * len_opp_moves)


class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves

        if len(legal_moves) == 0:
            return no_move

        strategy = self.alphabeta if self.method == 'alphabeta' else self.minimax

        best_move = no_move

        try:
            if self.iterative:
                depth = 1
                while True:
                    score, best_move = strategy(game, depth)
                    depth += 1
            else:
                score, best_move = strategy(game, self.search_depth)

        except Timeout:
            # Handle any actions required at timeout, if necessary
            return best_move

        return best_move

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        next_moves = game.get_legal_moves(game.active_player)

        if depth > 0 and len(next_moves) > 0:
            strategy = max if maximizing_player else min
            scores = [self.minimax(game.forecast_move(move), depth - 1, not maximizing_player)[0] for move in next_moves]
            score, best_move = strategy(zip(scores, next_moves), key=lambda x: x[0])
            return score, best_move
        else:
            # Terminate state --> return main_player's score
            return self.score(game, self), no_move

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        next_moves = game.get_legal_moves(game.active_player)

        if depth > 0 and len(next_moves) > 0:
            best_move = no_move
            best_score = float("-inf") if maximizing_player else float("inf")

            for move in next_moves:
                if maximizing_player:
                    move_score = self.alphabeta(game.forecast_move(move), depth - 1, alpha, beta, not maximizing_player)[0]
                    if move_score > best_score:
                        best_score = move_score
                        best_move = move

                    # best_score >= beta then it make no sense to continue because beta is upper bound
                    # of maximizing_player
                    if best_score >= beta:
                        return best_score, best_move

                    alpha = max(alpha, best_score)
                else:
                    move_score = self.alphabeta(game.forecast_move(move), depth - 1, alpha, beta, not maximizing_player)[0]
                    if move_score < best_score:
                        best_score = move_score
                        best_move = move

                    # best_score >= alpha then it make no sense to continue because alpha is lower bound
                    # of minimizing_player
                    if best_score <= alpha:
                        return best_score, best_move

                    beta = min(beta, best_score)

            return best_score, best_move
        else:
            # Terminate state --> return main_player's score
            return self.score(game, self), no_move
