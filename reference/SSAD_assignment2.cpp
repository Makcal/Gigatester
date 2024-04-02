#include <iostream> //importing necessary libraries
#include <string>
#include <fstream>
#include <vector>
#include <sstream>
#include <map>
#include <concepts>
#include <cstring>
#include <memory>
using namespace std;

vector<string> splitString(string& str) {
    istringstream ss(str);
    vector<string> tokens;
    string tok;
    while (ss >> tok) {
        if (!tok.empty()) {
            tokens.push_back(tok);
        }
    }
    return tokens;
}

class PhysicalItem;
class Weapon;
class Potion;
class Spell;

class Character {
    friend class Weapon;
    friend class Spell;
    friend class Potion;
    private:
        int healthPoints;
        string name;

    public:
        Character()=default;
        Character(int hp, string name) {
            this->healthPoints = hp;
            this->name = name;
        }

        string getName() {
            return name;
        }

        int getHP() {
            return healthPoints;
        }

        virtual void print(ofstream& os) {(void)os;}

        virtual bool getWeapon(shared_ptr<PhysicalItem> w, ofstream& os){
            (void)w;
            (void)os;
            return true;
        }

        virtual bool getPotion(shared_ptr<PhysicalItem> p, ofstream& os){
            (void)p;
            (void)os;
            return true;
        }

        virtual bool getSpell(shared_ptr<PhysicalItem> s, ofstream& os){
            (void)s;
            (void)os;
            return true;
        }

        virtual void showWeapons(ofstream& os){
            (void)os;
        }
        virtual void showSpells(ofstream& os){
            (void)os;
        }
        virtual void showPotions(ofstream& os){
            (void)os;
        }
        virtual string type(){ return "";}
        virtual int findWeapon(string item) {
            (void)item;
            return 0;
        }
        virtual shared_ptr<PhysicalItem> indWeapon(int i) {
            (void)i;
            return nullptr;
        }
        virtual int findPotion(string item) {
            (void)item;
            return 0;
        }
        virtual shared_ptr<PhysicalItem> indPotion(int i) {
            (void)i;
            return nullptr;
        }
        virtual int findSpell(string item) {
            (void)item;
            return 0;
        }
        virtual shared_ptr<PhysicalItem> indSpell(int i) {
            (void)i;
            return nullptr;
        }
    protected:
        void loseHP(int damage) {
            this->healthPoints -= damage;
        }

        void plusHP(int plus){
            this->healthPoints += plus;
        }
        virtual void empty() {}

        void death(ofstream& os) {
            os << name << " has died..." << endl;
            empty();
        }
        virtual void removePotion(string item) {
            (void)item;
        }
        virtual void removeSpell(string item) {
            (void)item;
        }
};

class PhysicalItem {
    friend class Character;
    protected:
        bool isUsableOnce;
        shared_ptr<Character> owner;
        string name;
    public:
        PhysicalItem()=default;
        PhysicalItem(bool isUsableOnce, shared_ptr<Character> owner, string name) {
            this->isUsableOnce = isUsableOnce;
            this->name = name;
            this->owner = owner;
        }
        virtual void use(shared_ptr<Character> target, ofstream& os){
            (void)target;
            (void)os;
        }

        string getName() {
            return name;
        }

        shared_ptr<Character> getOwner() {
            return owner;
        }

        virtual void print(ofstream& os) {
            (void)os;
        }
        virtual void atack() {}
        virtual bool hasTarget(shared_ptr<Character> ch2) {
            (void)ch2;
            return true;
        }
};

template<typename T>
concept Derived = std::is_base_of<PhysicalItem, T>::value == true;
class Weapon : public PhysicalItem {
    private:
        int damage;

    public:
        Weapon(shared_ptr<Character> owner, string name, int damage) : PhysicalItem(false, owner, name) {
            this->damage = damage;
        }
        int getDamage() {
            return damage;
        }
        void use(shared_ptr<Character> ch2, ofstream& os) {
            ch2.get()->loseHP(damage);
            if (ch2.get()->getHP() <= 0) {
                ch2.get()->death(os);
            }
        }
        void print(ofstream& os) {
            os << getName() <<  ":" << getDamage() << " ";
        }
};

class Potion : public PhysicalItem {
    private:
        int healValue;

    public:
        Potion(shared_ptr<Character> owner, string name, int healValue) : PhysicalItem(true, owner, name) {
            this->healValue = healValue;
        }
        int getHealValue() {
            return healValue;
        }
        void use(shared_ptr<Character> ch2, ofstream& os) {
            ch2.get()->plusHP(healValue);
            owner.get()->removePotion(name);
            (void)os;
        }

        void print(ofstream& os) {
            os << getName() <<  ":" << getHealValue() << " ";
        }
};

class Spell : public PhysicalItem {
    private:
        vector<shared_ptr<Character> > allowedTargets;

    public:
        Spell(shared_ptr<Character> owner, string name, vector<shared_ptr<Character> > allowedTargets) : PhysicalItem(true, owner, name) {
            this->allowedTargets = allowedTargets;
        }

        void print(ofstream& os) {
            os << getName() <<  ":" << allowedTargets.size() << " ";
        }
        bool hasTarget(shared_ptr<Character> ch2) {
            for (shared_ptr<Character> c : allowedTargets) {
                if (c.get()->getName() == ch2.get()->getName()) {
                    return true;
                }
            }
            return false;
        }

        void use(shared_ptr<Character> target, ofstream& os){
            target.get()->loseHP(target.get()->getHP());
            owner.get()->removeSpell(name);
            if (target.get()->getHP() <= 0) {
                target.get()->death(os);
            }
        }
};

template <typename T>
class Container {
    protected:
        vector<T> elements;
    public:
        bool find(T item) {
            if (find(elements.begin(), elements.end(), item) != elements.end()) {
                return true;
            }
            return false;
        }

        void removeItem(T newItem) {
            elements.pop_back(newItem);
        }

        void addItem(T newItem) {
            elements.push_back(newItem);
        }
};

template <>
class Container<PhysicalItem> {
    protected:
        vector<shared_ptr<PhysicalItem> > elements;
    public:
        shared_ptr<PhysicalItem> get(int i) {
            return elements[i];
        }

        int find(string itemName) {
            for (int i = 0; i < elements.size(); i++) {
                if (elements[i].get()->getName() == itemName) {
                    return i;
                }
            }
            return -1;
        }

        void removeItem(string itemName) {
            for (int i = 0; i < elements.size(); i++) {
                if (elements[i].get()->getName() == itemName) {
                    elements.erase(elements.begin() + i);
                    break;
                }
            }
        }

        int size() {
            return elements.size();
        }
};

void sortPSW(vector<shared_ptr<PhysicalItem> >& v) {
    int size = v.size();
    string temp;
    bool sw = true;
    while (sw) {
        sw = false;
        for (int i = 0; i < size - 1; i++) {
            if (strcmp(v[i].get()->getName().c_str(), v[i + 1].get()->getName().c_str()) > 0) {
                swap(v[i], v[i + 1]);
                sw = true;
            }
        }
    }
}

template <typename T> requires Derived<T>
class ContainerWithMaxCapacity : public Container<PhysicalItem> { 
    protected:
        int maxCapacity;
    public:
        bool addItem(shared_ptr<PhysicalItem> item, ofstream& os) {
            if (elements.size() < maxCapacity) {
                elements.push_back(move(item));
                return true;
            } else {
                os << "Error caught" << endl;
                return false;
            }
        }
        void show(ofstream& os) {
            sortPSW(elements);
            if (elements.size() == 0) {
                os << endl;
            } else {
                for(shared_ptr<PhysicalItem> el : elements) {
                    el.get()->print(os);
                }
                os << endl;
            }
        }
        
        void emptyItems() {
            elements.clear();
        }
 };

class Arsenal : public ContainerWithMaxCapacity<Weapon> {
    public:
    Arsenal()=default;
    Arsenal(int maxCapacity) {
        this->maxCapacity = maxCapacity;
    }
};

class SpellBook : public ContainerWithMaxCapacity<Spell> {
    public:
    SpellBook()=default;
    SpellBook(int maxCapacity) {
        this->maxCapacity = maxCapacity;
    }
};

class MedicalBag : public ContainerWithMaxCapacity<Potion> {
    public:
    MedicalBag()=default;
    MedicalBag(int maxCapacity) {
        this->maxCapacity = maxCapacity;
    }
};

class WeaponUser : virtual public Character {
    protected:
        Arsenal arsenal;
    public:
        WeaponUser(int hp, string name, int maxCap) : Character(hp, name), arsenal(maxCap){
        }

        bool getWeapon(shared_ptr<PhysicalItem> item, ofstream& os) {
            return arsenal.addItem(item, os);
        }
        void showWeapons(ofstream& os){
            arsenal.show(os);
        }
        int findWeapon(string item) {
            return arsenal.find(item);
        }
        shared_ptr<PhysicalItem> indWeapon(int i) {
            return arsenal.get(i);
        }
};

class PotionUser : virtual public Character {
    protected:
        MedicalBag medicalBag;
        void removePotion(string item) {
            medicalBag.removeItem(item);
        }
    public:
        PotionUser(int hp, string name, int maxCap) : Character(hp, name), medicalBag(maxCap) {

        }

        bool getPotion(shared_ptr<PhysicalItem> item, ofstream& os) {
            return medicalBag.addItem(item, os);
        }
        void showPotions(ofstream& os){
            medicalBag.show(os);
        }

        int findPotion(string item) {
            return medicalBag.find(item);
        }
        shared_ptr<PhysicalItem> indPotion(int i) {
            return medicalBag.get(i);
        }
};

class SpellUser : virtual public Character {
    protected:
        SpellBook spellBook;
        void removeSpell(string item) {
            spellBook.removeItem(item);
        }
    public:
        SpellUser(int hp, string name, int maxCap) : Character(hp, name), spellBook(maxCap) {

        }

        bool getSpell(shared_ptr<PhysicalItem> item, ofstream& os) {
            return spellBook.addItem(item, os);
        }
        void showSpells(ofstream& os){
            spellBook.show(os);
        }

        int findSpell(string item) {
            return spellBook.find(item);
        }
        shared_ptr<PhysicalItem> indSpell(int i) {
            return spellBook.get(i);
        }
};

class Fighter : public WeaponUser, public PotionUser {
    public:
        const static int maxAllowedWeapons = 3;
        const static int maxAllowedPotions = 5;
         Fighter(int hp, string name) : WeaponUser(hp, name, maxAllowedWeapons),
         PotionUser(hp, name, maxAllowedPotions), Character(hp, name) {
        }
        void print(ofstream& os) {
            os << getName() << ":fighter:" << getHP() << " ";
        }

        string type() {
            return "fighter";
        }

    private:
        void empty() {
            arsenal.emptyItems();
            medicalBag.emptyItems();
        }
};

class Archer : public WeaponUser, public PotionUser, public SpellUser {
    public:
        const static int maxAllowedWeapons = 2;
        const static int maxAllowedPotions = 3;
        const static int maxAllowedSpells = 2;
        Archer(int hp, string name) : WeaponUser(hp, name, maxAllowedWeapons), 
        PotionUser(hp, name, maxAllowedPotions), SpellUser(hp, name, maxAllowedSpells), Character(hp, name) {
        }
        void print(ofstream& os) {
            os << getName() << ":archer:" << getHP() << " ";
        }

        string type() {
            return "archer";
        }
    private:
        void empty() {
            arsenal.emptyItems();
            medicalBag.emptyItems();
            spellBook.emptyItems();
        }

};

class Wizard : public PotionUser, public SpellUser {
    public:
        const static int maxAllowedPotions = 10;
        const static int maxAllowedSpells = 10;
        Wizard(int hp, string name) : SpellUser(hp, name, maxAllowedSpells),
        PotionUser(hp, name, maxAllowedPotions), Character(hp, name) {
        }

        void print(ofstream& os) {
            os << getName() << ":wizard:" << getHP() << " ";
        }

        string type() {
            return "wizard";
        }

    private:
        void empty() {
            medicalBag.emptyItems();
            spellBook.emptyItems();
        }
};

void sortVectorOfChar(vector<shared_ptr<Character> >& v) {
    int size = v.size();
    string temp;
    bool sw = true;
    while (sw) {
        sw = false;
        for (int i = 0; i < size - 1; i++) {
            if (strcmp(v[i].get()->getName().c_str(), v[i + 1].get()->getName().c_str()) > 0) {
                swap(v[i], v[i + 1]);
                sw = true;
            }
        }
    }
}

int findChar(string name, vector<shared_ptr<Character> > v) {
    for (int i = 0; i < v.size(); i++) {
        if (v[i].get()->getName() == name) {
            return i;
        } 
    }
    return -1;
}

int main() {
    ifstream in;
    ofstream out;
    string line;
    string str;
    in.open ("input.txt");
    out.open ("output.txt");
    getline(in,line);
    int n = stoi(line);
    vector<shared_ptr<Character> > vectorOfChar;
    for (int i = 0; i < n; i++) {
        getline(in,line);
        vector<string> aboutChar = splitString(line);
        if (line.find("Create character") != string::npos) {
            out << "A new " << aboutChar[2] << " came to town, " << aboutChar[3] << "." << endl;
            if(aboutChar[2] == "fighter") {
                shared_ptr<Character> newChar(new Fighter(stoi(aboutChar[4]), aboutChar[3]));
                vectorOfChar.push_back(move(newChar));
            } else if (aboutChar[2] == "wizard") {
                shared_ptr<Character> newChar(new Wizard(stoi(aboutChar[4]), aboutChar[3]));
                vectorOfChar.push_back(move(newChar));
            } else if (aboutChar[2] == "archer") {
                shared_ptr<Character> newChar(new Archer(stoi(aboutChar[4]), aboutChar[3]));
                vectorOfChar.push_back(move(newChar));
            }
        } else if (line.find("Create item weapon") != string::npos) {
            if (findChar(aboutChar[3], vectorOfChar) != -1
            && vectorOfChar[findChar(aboutChar[3], vectorOfChar)].get()->type() != "wizard"
            && stoi(aboutChar[5]) > 0) {
                shared_ptr<PhysicalItem> newItem(new Weapon(vectorOfChar[findChar(aboutChar[3], vectorOfChar)], aboutChar[4], stoi(aboutChar[5])));
                bool f = vectorOfChar[findChar(aboutChar[3], vectorOfChar)].get()->getWeapon(newItem, out);
                if (f) {
                    out << aboutChar[3] << " just obtained a new weapon called " 
                    << aboutChar[4] << "." << endl;
                }
            } else {
                out << "Error caught" << endl;
            }
        } else if (line.find("Create item potion") != string::npos) {
            if (findChar(aboutChar[3], vectorOfChar) != -1 && stoi(aboutChar[5]) > 0) {
                shared_ptr<PhysicalItem> newItem(new Potion(vectorOfChar[findChar(aboutChar[3], vectorOfChar)], aboutChar[4], stoi(aboutChar[5])));
                bool f = vectorOfChar[findChar(aboutChar[3], vectorOfChar)].get()->getPotion(newItem, out);
                if (f) {
                    out << aboutChar[3] << " just obtained a new potion called " 
                    << aboutChar[4] << "." << endl;
                }
            } else {
                out << "Error caught" << endl;
            }
        } else if (line.find("Create item spell") != string::npos) {
            if (findChar(aboutChar[3], vectorOfChar) != -1
            && vectorOfChar[findChar(aboutChar[3], vectorOfChar)].get()->type() != "fighter") {
                vector<shared_ptr<Character> > targChar;
                bool flag =true;
                for (int q = 0; q < stoi(aboutChar[5]); q++) {
                    if (findChar(aboutChar[6 + q], vectorOfChar) != -1) {
                        targChar.push_back(vectorOfChar[findChar(aboutChar[6 + q], vectorOfChar)]);
                    } else {
                        flag = false;
                    }
                }
                shared_ptr<PhysicalItem> newItem(new Spell(vectorOfChar[findChar(aboutChar[3], vectorOfChar)],
                aboutChar[4], targChar));
                if (flag) {
                    bool f = vectorOfChar[findChar(aboutChar[3], vectorOfChar)].get()->getSpell(newItem, out);
                    if (f) {
                        out << aboutChar[3] << " just obtained a new spell called " 
                        << aboutChar[4] << "." << endl;
                    }
                } else {
                    out << "Error caught" << endl;
                }
            } else {
                out << "Error caught" << endl;
            }
        } else if (line.find("Attack") != string::npos) {
            int ch2 = findChar(aboutChar[2], vectorOfChar);
            int ch1 = findChar(aboutChar[1], vectorOfChar);
            if (ch2 != -1 && ch1 != -1
            && vectorOfChar[ch1].get()->type() != "wizard"
            && vectorOfChar[ch1].get()->findWeapon(aboutChar[3]) != -1) {
                int w1 = vectorOfChar[ch1].get()->findWeapon(aboutChar[3]);
                out << aboutChar[1] << " attacks " << aboutChar[2] 
                << " with their " << aboutChar[3] << "!" << endl;
                vectorOfChar[ch1].get()->indWeapon(w1).get()->use(vectorOfChar[ch2], out);
                if (vectorOfChar[ch2].get()->getHP() <= 0) {
                    for (int w = 0; w < vectorOfChar.size(); w++) {
                        if (vectorOfChar[w].get()->getName() == aboutChar[2]) {
                            vectorOfChar.erase(vectorOfChar.begin() + w);
                        } 
                    }
                }
            } else {
                out << "Error caught" << endl;
            }
        } else if (line.find("Cast") != string::npos) {
            int ch2 = findChar(aboutChar[2], vectorOfChar);
            int ch1 = findChar(aboutChar[1], vectorOfChar);
            if (ch2 != -1 && ch1 != -1
            && vectorOfChar[ch1].get()->type() != "fighter"
            && vectorOfChar[ch1].get()->findSpell(aboutChar[3]) != -1
            && vectorOfChar[ch1].get()->indSpell(vectorOfChar[ch1].get()->findSpell(aboutChar[3])).get()->hasTarget(vectorOfChar[ch2])) {
                int w1 = vectorOfChar[ch1].get()->findSpell(aboutChar[3]);
                out << aboutChar[1] << " casts " << aboutChar[3] 
                << " on " << aboutChar[2] << "!" << endl;
                vectorOfChar[ch1].get()->indSpell(w1).get()->use(vectorOfChar[ch2], out);
                for (int w = 0; w < vectorOfChar.size(); w++) {
                    if (vectorOfChar[w].get()->getName() == aboutChar[2]) {
                        vectorOfChar.erase(vectorOfChar.begin() + w);
                    } 
                }
            } else {
                out << "Error caught" << endl;
            }
        } else if (line.find("Drink") != string::npos) {
            int ch2 = findChar(aboutChar[2], vectorOfChar);
            int ch1 = findChar(aboutChar[1], vectorOfChar);
            if (ch2 != -1 && ch1 != -1
            && vectorOfChar[ch1].get()->findPotion(aboutChar[3]) != -1) {
                int w1 = vectorOfChar[ch1].get()->findPotion(aboutChar[3]);
                out << aboutChar[2] << " drinks " << aboutChar[3] 
                << " from " << aboutChar[1] << "." << endl;
                vectorOfChar[ch1].get()->indPotion(w1).get()->use(vectorOfChar[ch2], out);
            } else {
                out << "Error caught" << endl;
            }
        } else if (line.find("Dialogue") != string::npos) {
            if (aboutChar[1] == "Narrator" || findChar(aboutChar[1], vectorOfChar) != -1) {
                out << aboutChar[1] << ": ";
                for (int i = 0; i < stoi(aboutChar[2]); i++) {
                    out << aboutChar[3 + i] << " ";
                }
                out << endl; 
            } else {
                out << "Error caught" << endl;
            }
        } else if (line.find("Show characters") != string::npos) {
            sortVectorOfChar(vectorOfChar);
            for (int w = 0; w < vectorOfChar.size(); w++) {
                if (vectorOfChar[w].get()->getHP() > 0) {
                    vectorOfChar[w].get()->print(out);
                }
            }
            out << endl;
        } else if (line.find("Show weapons") != string::npos) {
            if (findChar(aboutChar[2], vectorOfChar) != -1 
            && vectorOfChar[findChar(aboutChar[2], vectorOfChar)].get()->type() != "wizard") {
                vectorOfChar[findChar(aboutChar[2], vectorOfChar)].get()->showWeapons(out);
            } else {
                out << "Error caught" << endl;
            }
        } else if (line.find("Show potions") != string::npos) {
            if (findChar(aboutChar[2], vectorOfChar) != -1) {
                vectorOfChar[findChar(aboutChar[2], vectorOfChar)].get()->showPotions(out);
            } else {
                out << "Error caught" << endl;
            }
        } else if (line.find("Show spells") != string::npos) {
            if (findChar(aboutChar[2], vectorOfChar) != -1
            && vectorOfChar[findChar(aboutChar[2], vectorOfChar)].get()->type() != "fighter") {
                vectorOfChar[findChar(aboutChar[2], vectorOfChar)].get()->showSpells(out);
            } else {
                out << "Error caught" << endl;
            }
        }
    }
    in.close();
    out.close();

    return 0;
}