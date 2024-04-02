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
        n = random.randint(1, 2000 if random.random() < 0.05 else 30)
        i = 0
        self.result = f"{n}\n"
        while i < n:
            """
Errors to be handled:

Character doesn't exist (Attack, Cast, Drink, Create item, spell target is not a character, Dialogue)
Character doesn't own an item (Attack, Cast, Drink).
Negative value or zero for a potion healValue (Create item potion).
Negative value or zero for a weapon's damageValue (Create item weapon).
Target is not in the list of allowed targets in casting spells (Cast).
Arsenal, MedicalBag, or SpellBook are full (Create item)
Character can't carry or use a certain item, e.g., wizards can't have weapons 
(show $itemType $characterName, Create Item, Attack, Cast).
            
            
"Create character $[string]type $[string]name $[int]initHP" (type can be fighter, wizard, or archer. 1≤initHP≤200
).
"Create item weapon $[string]ownerName $[string]weaponName $[int]damageValue" (1≤damageValue≤50
).
"Create item potion $[string]ownerName $[string]potionName $[int]healValue" (1≤healValue≤50
).
"Create item spell $[string]ownerName $[string]spellName $[int]m $[string_1, string_2, ..., string_m]characterNames" (set of 0≤m≤50
 unique characters names the spell can be applied on).
"Attack $[string]attackerName $[string]targetName $[string]weaponName" (attacker and target can be the same).
"Cast $[string]casterName $[string]targetName $[string]spellName" (caster and target can be the same).
"Drink $[string]supplierName $[string]drinkerName $[string]potionName" (supplier and drinker can be the same).
"Dialogue $[string]speaker (a character name or "Narrator") $[int]sp_len $[string_1, string_2, ..., string_sp_len]speech" (the speech itself where its length is sp_len, 1≤sp_len≤10
).
"Show characters" (show alive characters in alphabetical order).
"Show weapons $[string]characterName" (show weapons owned by characterName in alphabetical order).
"Show potions $[string]characterName" (show potions owned by characterName in alphabetical order).
"Show spells $[string]characterName" (show spells owned by characterName in alphabetical order).
The death of characters should be handled automatically.
"""
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
                m = random.randint(0, min(50, len(self.chars)))
                names = list(self.chars_names)
                random.shuffle(names)
                names = names[:m]
                if m != 0 and random.random() < 0.3:
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


__all__ = ['GeneratorSSADTask2']
