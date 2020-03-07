from .Cards_Base import *

expansions = [Base_Cards]
Cards = {name: card for exp in expansions for name, card in exp.items()}
