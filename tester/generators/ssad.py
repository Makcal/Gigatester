import dataclasses
import random
from typing import Literal

from .abs_generator import AbsGenerator


class GeneratorSSADTask2(AbsGenerator):
    @dataclasses.dataclass(frozen=True)
    class Item:
        type: Literal['weapon', 'potion', 'spell']
        name: str
        owner: "GeneratorSSADTask2.Character"

    @dataclasses.dataclass(frozen=True)
    class Character:
        name: str
        hp: int
        type: Literal["fighter", "wizard", "archer"]
        items: list["GeneratorSSADTask2.Item"] = dataclasses.field(default_factory=list)

    chars_names: set[str]
    item_names: set[str]
    chars: list[Character]
    items: list[Item]
    result: str
    valid_cmd: bool

    def __init__(self):
        self.chars_names = set()
        self.item_names = set()
        self.chars = []
        self.items = []
        self.result = ""
        self.valid_cmd = True

    def generate(self) -> str:
        self.chars_names = set()
        self.item_names = set()
        self.chars = []
        self.items = []
        self.result = ""
        self.valid_cmd = True
        n = random.randint(1, 200 if random.random() < 0.05 else 30)
        i = 0
        self.result = f"{n}\n"
        while i < n:
            self.valid_cmd = random.random() < 0.92
            if i == 0 and random.random() < 0.9:
                cmd = 'create_character'
            else:
                cmd = random.choices(
                    ['create_character', 'create_item', 'attack', 'cast', 'drink',
                     'say', 'show_characters', 'show_weapons', 'show_potions', 'show_spells'],
                    [18,                      35,            8,      6,        8,
                     4,        6,                  6,              6,            6],
                )[0]
            res = getattr(self, cmd)()
            self.result += res + '\n'
            i += 1

        return self.result

    CHAR_TYPES = ("fighter", "wizard", "archer")

    def create_character(self) -> str:
        t = random.choice(self.CHAR_TYPES)
        n = self.get_char_name()
        h = random.randint(1, 200)

        self.chars_names.add(n)
        self.chars.append(self.Character(n, h, t))
        return f"Create character {t} {n} {h}"

    ITEM_TYPES = ("weapon", "potion", "spell")

    def create_item(self) -> str:
        t = random.choices(self.ITEM_TYPES, [1, 5, 3])[0]
        if random.random() < 0.9 and self.chars:
            owner: "GeneratorSSADTask2.Character" = random.choice(self.chars)
        else:
            owner = self.Character("notexists", 1, 'fighter')
        n = self.get_item_name()
        self.item_names.add(n)
        i = self.Item(t, n, owner)
        owner.items.append(i)
        self.items.append(i)
        match t:
            case "weapon":
                d = random.randint(-5, 50)
                return f"Create item weapon {owner.name} {n} {d}"
            case "potion":
                h = random.randint(-5, 50)
                return f"Create item potion {owner.name} {n} {h}"
            case "spell":
                t = min(50, len(self.chars))
                if not t:
                    return f"Create item spell uwu {n} 1 uwu"
                else:
                    m = random.randint(1, t)
                names = list(self.chars_names)
                random.shuffle(names)
                names = names[:m]
                if random.random() < 0.3:
                    names[0] = self.get_char_name()
                return f"Create item spell {owner.name} {n} {m} {' '.join(names)}"

    def attack(self) -> str:
        attacker = self.choose_char()
        if random.random() < 0.95 and len(attacker.items):
            wn = random.choice(attacker.items).name
        else:
            wn = 'notexists' if random.random() < 0.5 or not self.items else random.choice(self.items).name
        target = self.choose_char()
        return f"Attack {attacker.name} {target.name} {wn}"

    def cast(self) -> str:
        attacker = self.choose_char()
        if random.random() < 0.95 and len(attacker.items):
            sn = random.choice(attacker.items).name
        else:
            sn = 'notexists' if random.random() < 0.5 or not self.items else random.choice(self.items).name
        target = self.choose_char()
        return f"Cast {attacker.name} {target.name} {sn}"

    def drink(self) -> str:
        supplier = self.choose_char()
        if random.random() < 0.95 and len(supplier.items):
            dn = random.choice(supplier.items).name
        else:
            dn = 'notexists' if random.random() < 0.5 or not self.items else random.choice(self.items).name
        target = self.choose_char()
        return f"Drink {supplier.name} {target.name} {dn}"

    def say(self) -> str:
        if random.random() < 0.8 and self.chars:
            speaker = random.choice(self.chars)
        elif random.random() < 0.6:
            speaker = self.Character('Narrator', 1, 'fighter')
        else:
            speaker = self.Character('notexists', 1, 'fighter')
        n = random.randint(1, 10)
        msg = ['bla'] * n
        return f"Dialogue {speaker.name} {n} {' '.join(msg)}"

    def show_characters(self) -> str:
        return "Show characters"

    def show_weapons(self) -> str:
        n = self.choose_char().name
        return f"Show weapons {n}"

    def show_potions(self) -> str:
        n = self.choose_char().name
        return f"Show potions {n}"

    def show_spells(self) -> str:
        n = self.choose_char().name
        return f"Show spells {n}"

    CHAR_NAMES = ("max", "munir", "harry", "oleg", "cat", "mummy", "zlata", "dd", "dan")
    ITEM_NAMES = ("sword", "arbuz", "wand", "pen", "laser", "rocket", "bdsm")
    ALPH = 'abcerwocnspq'

    def get_random_name(self):
        sl = list(self.ALPH)
        random.shuffle(sl)
        s = ''.join(sl[:random.randint(3, 10)])
        return s

    def get_char_name(self):
        i = 0
        while i < len(self.CHAR_NAMES) and self.CHAR_NAMES[i] in self.chars_names:
            i += 1
        if i == len(self.CHAR_NAMES):
            s = self.get_random_name()
            while s in self.chars_names:
                s = self.get_random_name()
            return s
        else:
            return self.CHAR_NAMES[i]

    def get_item_name(self):
        i = 0
        while i < len(self.ITEM_NAMES) and self.ITEM_NAMES[i] in self.item_names:
            i += 1
        if i == len(self.ITEM_NAMES):
            s = self.get_random_name()
            while s in self.item_names:
                s = self.get_random_name()
            return s
        else:
            return self.ITEM_NAMES[i]

    def choose_char(self):
        if random.random() < 0.95 and self.chars:
            c = random.choice(self.chars)
        else:
            c = self.Character('notexists', 1, 'fighter')
        return c


class GeneratorSSADTask3(AbsGenerator):
    chars_names: set[str]

    def __init__(self):
        self.chars_names = set()
        self.result = ""

    def generate(self) -> str:
        self.chars_names = set()
        self.result = ""
        n = random.randint(1, 200 if random.random() < 0.05 else 40)
        i = 0
        self.result = f"{n}\n"
        while i < n:
            if i == 0 and random.random() < 0.9:
                cmd = 'create_account'
            else:
                cmd = random.choices(
                    ['create_account', 'deposit', 'withdraw', 'transfer', 'view', 'deactivate', 'activate'],
                    [15,                  5,          3,           3,        3,        3,            3],
                )[0]
            res = getattr(self, cmd)()
            self.result += res + '\n'
            i += 1

        return self.result

    @staticmethod
    def get_float(a: int, b: int) -> float:
        return random.randint(2*a, 2*b) / 2

    ACC_TYPES = ("Savings", "Checking", "Business")

    def create_account(self) -> str:
        type = random.choice(self.ACC_TYPES)
        name = self.get_name()
        initial_dep = self.get_float(1, 450)

        self.chars_names.add(name)
        return f"Create Account {type} {name} {initial_dep}"

    def deposit(self) -> str:
        depositor = self.choose_char()
        amount = self.get_float(1, 450)
        return f"Deposit {depositor} {amount}"

    def withdraw(self) -> str:
        user = self.choose_char()
        amount = self.get_float(1, 150 if random.random() < 0.66 else 5000)
        return f"Withdraw {user} {amount}"

    def transfer(self) -> str:
        user = self.choose_char()
        target = self.choose_char()
        amount = self.get_float(1, 150 if random.random() < 0.66 else 5000)
        return f"Transfer {user} {target} {amount}"

    def view(self) -> str:
        name = self.choose_char()
        return f"View {name}"

    def deactivate(self) -> str:
        name = self.choose_char()
        return f"Deactivate {name}"

    def activate(self) -> str:
        name = self.choose_char()
        return f"Activate {name}"

    CHAR_NAMES = ("max", "munir", "john", "bob", "alice", "vanya", "mazhor", "arbuz", "shizov", "marco")
    ALPH = 'abcerwocnspq'

    def get_random_name(self):
        sl = list(self.ALPH)
        random.shuffle(sl)
        s = ''.join(sl[:random.randint(3, 10)])
        return s

    def get_name(self):
        i = 0
        while i < len(self.CHAR_NAMES) and self.CHAR_NAMES[i] in self.chars_names:
            i += 1
        if i == len(self.CHAR_NAMES):
            s = self.get_random_name()
            while s in self.chars_names:
                s = self.get_random_name()
            return s
        else:
            return self.CHAR_NAMES[i]

    def choose_char(self):
        if random.random() < 0.95 and self.chars_names:
            c = random.choice(tuple(self.chars_names))
        else:
            c = 'notexists'
        return c


__all__ = ['GeneratorSSADTask2', 'GeneratorSSADTask3']
