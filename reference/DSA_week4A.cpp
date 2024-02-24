// Author: Maxim Fomin
#include <iostream>
#include <malloc.h>
#include <stdexcept>
#include <string.h>

using namespace std;

template<typename T>
class ListNode {
public:
    ListNode<T>* next;
    ListNode<T>* prev;
    T* value;

    ListNode(T* value) {
        this->value = value;
    }
};

template<typename T>
class ListIterator {
private:
    ListNode<T>* current;

public:
    ListIterator(ListNode<T>* start) {
        current = start;
    }

    ListIterator<T>& operator++() {
        current = current->next;
        return *this;
    }

    T& operator*() {
        return *current->value;
    }

    bool operator!=(ListIterator<T>& other) {
        return current != other.current;
    }
};

template<typename T>
class List {
public:
    virtual int getSize() = 0;

    virtual void pushBack(T element) = 0;

    virtual bool removeFirst(T element) = 0;

    virtual ListIterator<T> begin() = 0;

    virtual ListIterator<T> end() = 0;
};

// represents a circular doubly linked list with a sentinel
template<typename T>
class LinkedList : public List<T> {
private:
    int size = 0;
    ListNode<T>* sentinel;

public:
    LinkedList() {
        sentinel = new ListNode<T>(nullptr);
        sentinel->next = sentinel;
        sentinel->prev = sentinel;
    }

    int getSize() {
        return size;
    }

    void pushBack(T element) {
        T* ep = (T*)malloc(sizeof(T));
        *ep = element;
        ListNode<T>* new_node = new ListNode<T>(ep);
        new_node->prev = sentinel->prev;
        new_node->next = sentinel;
        sentinel->prev->next = new_node;
        sentinel->prev = new_node;
        size++;
    }

    bool removeFirst(T element) {
        ListNode<T>* node = sentinel->next;
        while (node != sentinel)
        {
            if (*node->value == element) {
                node->next->prev = node->prev;
                node->prev->next = node->next;
                free(node);
                return true;
            }
            node = node->next;
        }
        return false;
    }

    ListIterator<T> begin() {
        return ListIterator<T>(sentinel->next);
    }

    ListIterator<T> end() {
        return ListIterator<T>(sentinel);
    }
};

template<typename K, typename V>
struct KeyValuePair {
public:
    K key;
    V value;

    KeyValuePair() {}

    KeyValuePair(K k, V v) {
        key = k;
        value = v;
    }

    bool operator==(KeyValuePair<K, V>& other) {
        return key == other.key && value == other.value;
    }

    void operator=(KeyValuePair<K, V> &o) {
        this->key = o.key;
        this->value = o.value;
    }
};

template<typename K, typename V>
class Map {
public:
    virtual int getSize() = 0;

    virtual void put(K key, V value) = 0;

    virtual V get(K key) = 0;

    virtual List<KeyValuePair<K, V>>* getEntrySet() = 0;
};

template<typename K, typename V>
class HashMap : public Map<K, V> {
private:
    int size = 0;
    int table_size = 13;
    List<KeyValuePair<K, V>>** table;

    template<typename T>
    static int hash(T object) {
        return abs((int)std::hash<T>()(object));
    }

    static bool putIntoTable(KeyValuePair<K, V> pair, List<KeyValuePair<K, V>>** table, int table_size) {
        bool replaced = false;
        int slot = hash<K>(pair.key) % table_size;
        for (KeyValuePair<K, V> p : *table[slot]) {
            if (p.key == pair.key) {
                replaced = table[slot]->removeFirst(p);
                break;
            }
        }
        table[slot]->pushBack(pair);
        return replaced;
    }

    void resize(int new_size) {
        auto new_table = (List<KeyValuePair<K, V>>**)malloc(sizeof(LinkedList<KeyValuePair<K, V>>*) * new_size);
        for (int i = 0; i < new_size; i++) {
            new_table[i] = new LinkedList<KeyValuePair<K, V>>();
        }
        for (auto pair : *getEntrySet()) {
            putIntoTable(pair, new_table, new_size);
        }

        table = new_table;
        table_size = new_size;
    }

public:
    HashMap() {
        table = (List<KeyValuePair<K, V>>**)malloc(sizeof(LinkedList<KeyValuePair<K, V>>*) * table_size);
        for (int i = 0; i < table_size; i++) {
            table[i] = new LinkedList<KeyValuePair<K, V>>();
        }
    }

    int getSize(){
        return size;
    }

    void put(K key, V value) {
        if (size >= 4 * table_size) {
            resize(table_size * 2);
        }
        if (!putIntoTable(KeyValuePair<K, V>(key, value), table, table_size))
            size++;
    }

    V get(K key) {
        int slot = hash<K>(key) % table_size;
        for (KeyValuePair<K, V> p : *table[slot]) {
            if (p.key == key) {
                return p.value;
            }
        }
        while (1);
        throw runtime_error("No such key");
    }

    bool hasKey(K key) {
        int slot = hash<K>(key) % table_size;
        for (KeyValuePair<K, V> p : *table[slot]) {
            if (p.key == key) {
                return true;
            }
        }
        return false;
    }

    List<KeyValuePair<K, V>>* getEntrySet() {
        auto list = new LinkedList<KeyValuePair<K, V>>();

        for (int i = 0; i < table_size; i++) {
            for (auto pair : *table[i]) {
                list->pushBack(pair);
            }
        }

        return list;
    }
};

// merge sort
template<typename T>
void sort(T* array, int l, int r, int(comp)(T&, T&)) {
    if (r - l == 1) return;
    sort(array, l, (r+l)/2, comp);
    sort(array, (r+l)/2, r, comp);
    T t[r-l];
    int i = l;
    int j = (r+l)/2;
    for (int k = 0; k < r-l; k++) {
        if (j == r || i < (r+l)/2 && comp(array[i], array[j]) <= 0) {
            t[k] = array[i++];
        }
        else {
            t[k] = array[j++];
        }
    }
    for (int k = 0; k < r-l; k++) {
        array[l+k] = t[k];
    }
}

class MyString {
public:
    char* s;

    bool operator==(MyString o) {
        return strcmp(s, o.s) == 0;
    }

    int operator>(MyString o) {
        return strcmp(s, o.s);
    }
};

// Medians-of-medians (see https://en.wikipedia.org/wiki/Median_of_medians)

int partition5(int* list, int left, int right) {
    int i = left + 1;
    while (i <= right) {
        int j = i;
        while (j > left && list[j-1] > list[j]) {
            swap(list[j-1], list[j]);
            j--;
        }
        i++;
    }
    return (left + right) / 2;
}

int partition(int* list, int left, int right, int pivotIndex, int n) {
    int pivotValue = list[pivotIndex];
    swap(list[pivotIndex], list[right]);  // Move pivot to end
    int storeIndex = left;

    // Move all elements smaller than the pivot to the left of the pivot
    for (int i = left; i < right; i++) {
        if (list[i] < pivotValue) {
            swap(list[storeIndex], list[i]);
            storeIndex++;
        }
    }

    // Move all elements equal to the pivot right after
    // the smaller elements
    int storeIndexEq = storeIndex;
    for (int i = storeIndex; i < right; i++) {
        if (list[i] == pivotValue) {
            swap(list[storeIndexEq], list[i]);
            storeIndexEq++;
        }
    }

    // Move pivot to its final place
    swap(list[right], list[storeIndexEq]);
    // Return location of pivot considering the desired location n
    if (n < storeIndex) {
        return storeIndex;  // n is in the group of smaller elements
    }
    if (n <= storeIndexEq) {
        return n;  // n is in the group equal to pivot
    }
    return storeIndexEq;  // n is in the group of larger elements
}

int select(int* list, int left, int right, int n);

int pivot(int* list, int left, int right) {
    // for 5 or less elements just get median
    if (right - left < 5) {
        return partition5(list, left, right);
    }

    // otherwise move the medians of five-element subgroups to the first n/5 positions
    for (int i = left; i <= right; i += 5) {
        // get the median position of the i'th five-element subgroup
        int subRight = i + 4;
        if (subRight > right) {
            subRight = right;
        }
        int median5 = partition5(list, i, subRight);
        swap(list[median5], list[left + (i - left) / 5]);
    }

    // compute the median of the n/5 medians-of-five
    int mid = (right - left) / 10 + left + 1;
    return select(list, left, left + (right - left) / 5, mid);
}

int select(int* list, int left, int right, int n) {
    while (true) {
        if (left == right) {
            return left;
        }
        int pivotIndex = pivot(list, left, right);
        pivotIndex = partition(list, left, right, pivotIndex, n);
        if (n == pivotIndex) {
            return n;
        }
        else if (n <= pivotIndex) {
            right = pivotIndex - 1;
        }
        else {
            left = pivotIndex + 1;
        }
    }
}

int nthSmallest(int* list, int length, int n) {
    int index = select(list, 0, length-1, n);
    return list[index];
}

struct Student {
    int rating;
    char* name;

    Student() {
        name = new char[50];
    }

    bool operator==(Student& other) {
        return rating == other.rating;
    }
};

int main() {
    // I/O speed up
    ios_base::sync_with_stdio(0);
    cin.tie(0);
    cout.tie(0);

    int n;
    cin >> n;
    int a[n];
    HashMap<int, Student> map;
    for (int i = 0; i < n; i++) {
        cin >> a[i];
        Student s;
        char t[25];
        s.rating = a[i];
        cin >> s.name >> t;
        strcat(s.name, " ");
        strcat(s.name, t);
        map.put(s.rating, s);
    }
    cout << map.get(nthSmallest(a, n, n/2)).name << endl;
}
