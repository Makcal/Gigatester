// Author: Maxim Fomin
#include <iostream>
#include <vector>
#include <functional>

using namespace std;

template<typename T>
class LinkedList;

template<typename T>
class ListNode {
public:
    ListNode<T>* next;
    ListNode<T>* prev;
    T* value;

    explicit ListNode(T* value) {
        this->value = value;
    }

    ~ListNode() {
        delete value;
    }
};

template<typename T>
class ListIterator {
private:
    ListNode<T>* current;
    friend LinkedList<T>;

public:
    explicit ListIterator(ListNode<T>* start) {
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

    virtual void pushBack(const T& element) = 0;

    virtual void remove(const ListIterator<T>& iterator) = 0;

    virtual bool removeFirst(const T& element) = 0;

    virtual ListIterator<T> begin() = 0;

    virtual ListIterator<T> end() = 0;

    [[nodiscard]] virtual const ListIterator<T> begin() const = 0;

    [[nodiscard]] virtual const ListIterator<T> end() const = 0;
};

// represents a circular doubly linked list with a sentinel
template<typename T>
class LinkedList : public List<T> {
private:
    int size = 0;
    ListNode<T>* sentinel;

    void removeNode(ListNode<T>* node) {
        if (node == sentinel) return;
        node->next->prev = node->prev;
        node->prev->next = node->next;
        size--;
        delete node;
    }

public:
    LinkedList() {
        sentinel = new ListNode<T>(nullptr);
        sentinel->next = sentinel;
        sentinel->prev = sentinel;
    }

    LinkedList(const LinkedList<T>& other) : LinkedList() {
        clear();
        for (auto it : other) {
            auto ep = new T(it);
            auto new_node = new ListNode<T>(ep);
            new_node->prev = sentinel->prev;
            new_node->next = sentinel;
            sentinel->prev->next = new_node;
            sentinel->prev = new_node;
            size++;
        }
    }

    void clear() {
        if (size == 0) return;

        ListNode<T>* current = sentinel->prev;
        ListNode<T>* next = current->prev;
        while (current != sentinel) {
            delete current;
            current = next;
            next = next->prev;
        }
        sentinel->prev = sentinel->next = sentinel;
    }

    ~LinkedList() {
        if (size == 0) {
            delete sentinel;
            return;
        }
        clear();
        delete sentinel;
    }

    int getSize() override {
        return size;
    }

    void pushBack(const T& element) override {
        auto ep = new T(element);
        auto new_node = new ListNode<T>(ep);
        new_node->prev = sentinel->prev;
        new_node->next = sentinel;
        sentinel->prev->next = new_node;
        sentinel->prev = new_node;
        size++;
    }

    void remove(const ListIterator<T> &it) override {
        if (it.current == sentinel) return;
        removeNode(it.current);
    }

    bool removeFirst(const T& element) override {
        ListNode<T>* node = sentinel->next;
        while (node != sentinel)
        {
            if (*node->value == element) {
                removeNode(node);
                return true;
            }
            node = node->next;
        }
        return false;
    }

    ListIterator<T> begin() override {
        return ListIterator<T>(sentinel->next);
    }

    ListIterator<T> end() override {
        return ListIterator<T>(sentinel);
    }

    [[nodiscard]] const ListIterator<T> begin() const override {
        return ListIterator<T>(sentinel->next);
    }

    [[nodiscard]] const ListIterator<T> end() const override {
        return ListIterator<T>(sentinel);
    }
};

template<typename K, typename V>
struct KeyValuePair {
public:
    K key;
    V value;

    KeyValuePair() = default;

    KeyValuePair(K k, V v) {
        key = k;
        value = v;
    }

    bool operator==(const KeyValuePair<K, V>& other) const {
        return key == other.key && value == other.value;
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

    int getSize() override{
        return size;
    }

    void put(K key, V value) override {
        if (size >= 4 * table_size) {
            resize(table_size * 2);
        }
        if (!putIntoTable(KeyValuePair<K, V>(key, value), table, table_size))
            size++;
    }

    V get(K key) override {
        int slot = hash<K>(key) % table_size;
        for (KeyValuePair<K, V> p : *table[slot]) {
            if (p.key == key) {
                return p.value;
            }
        }
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

    List<KeyValuePair<K, V>>* getEntrySet() override {
        auto list = new LinkedList<KeyValuePair<K, V>>();

        for (int i = 0; i < table_size; i++) {
            for (auto pair : *table[i]) {
                list->pushBack(pair);
            }
        }

        return list;
    }
};

template <typename VT, typename ET>
class Graph {
public:
    struct Edge {
        ET label;
        int from, to;

        Edge(ET label, int from, int to) : label(label), from(from), to(to) {}

        bool operator==(const Edge& other) {
            return from == other.from && to == other.to;
        }
    };

private:
    HashMap<VT, int> vertexMapping;
    vector<VT> vertices;
    vector<ET> edges;

    vector<LinkedList<Edge>> adjacencyLists;

public:
    int addVertex(VT label) {
        int i = vertexMapping.getSize();
        vertexMapping.put(label, i);
        vertices.push_back(label);
        adjacencyLists.push_back(LinkedList<Edge>());
        return i;
    }

    void addEdge(ET label, VT from, VT to) {
        int f = vertexMapping.get(from);
        int t = vertexMapping.get(to);
        Edge edge(label, f, t);
        edges.push_back(label);
        adjacencyLists[f].pushBack(edge);
    }

    const LinkedList<Edge>& adjacentEdges(VT vertex) {
        return adjacencyLists[vertexMapping.get(vertex)];
    }

    void MaximFomin_bfs(VT start, function<void(const VT&)> visit) {
        vector<char> visited(vertices.size(), 0);
        LinkedList<VT> queue;
        queue.pushBack(start);
        while (queue.getSize()) {
            VT v = *queue.begin();
            queue.remove(queue.begin());
            visited[vertexMapping.get(v)] = true;
            visit(v);
            for (auto it : adjacentEdges(v)) {
                if (visited[vertexMapping.get(vertices[it.to])]) continue;
                queue.pushBack(vertices[it.to]);
            }
        }
    }
};

int main() {
    // I/O speed up
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);

    int n;
    cin >> n;
    Graph<int, char> graph;
    for (int i = 0; i < n; i++) {
        graph.addVertex(i);
    }
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            int x;
            cin >> x;
            if (x != 0) {
                graph.addEdge('E', i, j);
                graph.addEdge('E', j, i);
            }
        }
    }
    vector<char> visited(n, 0);
    graph.MaximFomin_bfs(0, function<void(const int&)>([&visited](int i){ visited[i] = true; }));
    bool ok = true;
    for (int i = 0; i < n; i++) {
        ok = ok && visited[i];
    }

    cout << (ok ? "YES" : "NO");

    return 0;
}
