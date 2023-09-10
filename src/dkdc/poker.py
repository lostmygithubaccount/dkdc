# imports
import re
from rich import console

from texasholdem.game.game import TexasHoldEm
from texasholdem.gui.text_gui import TextGUI
from texasholdem.agents import call_agent, random_agent
from texasholdem.evaluator import rank_to_string as _rank_to_string

# setup console
console = console.Console()


# configure poker
game = TexasHoldEm(buyin=10000, big_blind=5, small_blind=2, max_players=8)
# gui = TextGUI(game=game)


def rank_to_string(rank):
    if rank is None:
        return ""
    elif rank == -1:
        return "no contest"
    return _rank_to_string(rank)


def play_poker() -> list:
    session_history = []
    while game.is_game_running():
        game.start_hand()
        while game.is_hand_running():
            if game.current_player == 0:
                action, total = call_agent(game)
                game.take_action(action, total=total)
                # gui.refresh()
            elif game.current_player == 1:
                action, total = random_agent(game)
                game.take_action(action, total=total)
            else:
                action, total = random_agent(game)
                game.take_action(action, total=total)
                # gui.refresh()
                # gui.run_step()
        session_history.append(game.hand_history)

    return session_history


# functions
def poker_total():
    path = "poker.md"
    total = 0
    pattern = r"\d{1,2}\/\d{1,2}:\s*([+-]?\d+)"

    with open(path, "r") as file:
        contents = file.read()
        matches = re.findall(pattern, contents)
        for match in matches:
            num = int(match)
            total += num

    color = "green" if total >= 0 else "red"
    console.print(f"[bold {color}]Earnings: {total}[/bold {color}]")


# functions
def history_to_dict(history):
    if history is None:
        return {}
    return {
        "prehand": prehand_to_dict(history.prehand),
        "preflop": betting_round_to_dict(history.preflop),
        "flop": betting_round_to_dict(history.flop),
        "turn": betting_round_to_dict(history.turn),
        "river": betting_round_to_dict(history.river),
        "settle": settle_to_dict(history.settle),
    }


def prehand_to_dict(prehand):
    if prehand is None:
        return {}
    return {
        "btn_loc": prehand.btn_loc,
        "big_blind": prehand.big_blind,
        "small_blind": prehand.small_blind,
        "player_chips": prehand.player_chips,
        "player_cards": {
            player_id: cards_to_str(player_cards)
            for player_id, player_cards in prehand.player_cards.items()
        },
    }


def betting_round_to_dict(betting_round):
    if betting_round is None:
        return {}
    return {
        "new_cards": cards_to_str(betting_round.new_cards),
        "actions": [action_to_dict(action) for action in betting_round.actions],
    }


def cards_to_str(cards: list) -> list[str]:
    if cards is None:
        return []
    elif cards == []:
        return []
    return [card_to_str(card) for card in cards]


def card_to_str(card) -> str:
    return str(card)


def action_to_dict(action):
    if action is None:
        return {}
    return {
        "player_id": action.player_id,
        "action_type": {
            "name": action.action_type.name,
            "value": action.action_type.value,
            "player_id": action.player_id,
            "total": action.total,
        },
    }


def settle_to_dict(settle):
    if settle is None:
        return {}
    pot_winners = {a: [*b, rank_to_string(b[1])] for a, b in settle.pot_winners.items()}

    return {
        "new_cards": cards_to_str(settle.new_cards),
        "pot_winners": pot_winners,
    }
