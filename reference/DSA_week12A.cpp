// Author: Maxim Fomin
#include <bits/stdc++.h>

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

    explicit ListIterator(ListNode<T>* start) {
        current = start;
    }

public:
    ListIterator<T>& operator++() {
        current = current->next;
        return *this;
    }

    T& operator*() {
        return *current->value;
    }

    bool operator!=(const ListIterator<T>& other) {
        return current != other.current;
    }
};


template <typename T>
class ConstListIterator {
private:
    ListNode<T>* current;

    friend LinkedList<T>;

    explicit ConstListIterator(ListNode<T>* start) {
        current = start;
    }

public:
    ConstListIterator& operator++() {
        current = current->next;
        return *this;
    }

    const T& operator*() {
        return *current->value;
    }

    bool operator!=(const ConstListIterator& other) {
        return current != other.current;
    }
};


// represents a circular doubly linked list with a sentinel
template<typename T>
class LinkedList {
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

    int getSize() {
        return size;
    }

    void pushBack(const T& element) {
        auto ep = new T(element);
        auto new_node = new ListNode<T>(ep);
        new_node->prev = sentinel->prev;
        new_node->next = sentinel;
        sentinel->prev->next = new_node;
        sentinel->prev = new_node;
        size++;
    }

    void remove(const ListIterator<T> &it) {
        if (it.current == sentinel) return;
        removeNode(it.current);
    }

    bool removeFirst(const T& element) {
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

    ListIterator<T> begin() {
        return ListIterator<T>(sentinel->next);
    }

    ListIterator<T> end() {
        return ListIterator<T>(sentinel);
    }

    [[nodiscard]] ConstListIterator<T> begin() const {
        return ConstListIterator<T>(sentinel->next);
    }

    [[nodiscard]] ConstListIterator<T> end() const {
        return ConstListIterator<T>(sentinel);
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
class HashMap {
private:
    int size = 0;
    int table_size = 13;
    LinkedList<KeyValuePair<K, V>>** table;

    template<typename T>
    static int hash(T object) {
        return abs((int)std::hash<T>()(object));
    }

    static bool putIntoTable(const KeyValuePair<K, V>& pair, LinkedList<KeyValuePair<K, V>>** table, int table_size) {
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
        auto new_table = (LinkedList<KeyValuePair<K, V>>**) malloc(sizeof(LinkedList<KeyValuePair<K, V>>*) * new_size);
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
        table = (LinkedList<KeyValuePair<K, V>>**) malloc(sizeof(LinkedList<KeyValuePair<K, V>>*) * table_size);
        for (int i = 0; i < table_size; i++) {
            table[i] = new LinkedList<KeyValuePair<K, V>>();
        }
    }

    int getSize() {
        return size;
    }

    void put(const K& key, const V& value) {
        if (size >= 4 * table_size) {
            resize(table_size * 2);
        }
        if (!putIntoTable(KeyValuePair<K, V>(key, value), table, table_size))
            size++;
    }

    V get(const K& key) {
        int slot = hash<K>(key) % table_size;
        for (KeyValuePair<K, V> p : *table[slot]) {
            if (p.key == key) {
                return p.value;
            }
        }
        throw runtime_error("No such key");
    }

    bool hasKey(const K& key) {
        int slot = hash<K>(key) % table_size;
        for (KeyValuePair<K, V> p : *table[slot]) {
            if (p.key == key) {
                return true;
            }
        }
        return false;
    }

    LinkedList<KeyValuePair<K, V>>* getEntrySet() {
        auto list = new LinkedList<KeyValuePair<K, V>>();

        for (int i = 0; i < table_size; i++) {
            for (auto pair : *table[i]) {
                list->pushBack(pair);
            }
        }

        return list;
    }
};


/*
 * Standard comparing convention: less
 * true means <
 */
template <typename T>
class BinaryHeap {
private:
    typedef function<bool(const T&, const T&)> comparator_type;

    vector<T> tree;
    comparator_type comparator;

    /*
     * UB if i == 0
     */
    inline int parent(int i) {
        return (i-1) / 2;
    }

    inline int left_child(int i) {
        return i*2 + 1;
    }

    inline int right_child(int i) {
        return i*2 + 2;
    }

    void heapify(int i) {
        int l = left_child(i);
        int r = right_child(i);
        int largest_child = i;
        if (l < tree.size() && comparator(tree[largest_child], tree[l])) {
            largest_child = l;
        }
        if (r < tree.size() && comparator(tree[largest_child], tree[r])) {
            largest_child = r;
        }
        if (largest_child == i) {
            return;
        }
        swap(tree[i], tree[largest_child]);
        heapify(largest_child);
    }

public:
    explicit BinaryHeap(const vector<T>& initial = {}, const comparator_type& comparator = less<T>())
            : tree(initial), comparator(std::move(comparator)) {
        for (int i = initial.size() / 2 - 1; i >= 0; i--) {
            heapify(i);
        }
    }

    void put(const T& element) {
        int i = tree.size();
        tree.push_back(element);
        while (i != 0 && comparator(tree[parent(i)], element)) {
            swap(tree[parent(i)], tree[i]);
            i = parent(i);
        }
    }

    [[nodiscard]] inline int size() const {
        return tree.size();
    }

    [[nodiscard]] inline const T& top() const {
        return tree[0];
    }

    void popTop() {
        tree[0] = tree[tree.size()-1];
        tree.pop_back();
        heapify(0);
    }
};


template <typename VT, typename ET>
class Graph {
public:
    struct Edge {
    private:
        int from, to;

    public:
        ET data;

        friend Graph;

        Edge(ET data, int from, int to) : data(std::move(data)), from(from), to(to) {}

        bool operator==(const Edge& other) {
            return from == other.from && to == other.to;
        }
    };

private:
    HashMap<VT, int> vertexMapping;
    vector<VT> vertices;
    vector<ET> edges;
    vector<LinkedList<Edge>> adjacencyLists;

    /*
     * minimal_edge_weight, vertex_index, parent
     */
    using helpTuple = tuple<int, int, const Edge*>;

    void addEdge1(const Edge& edge) {
        edges.push_back(edge.data);
        adjacencyLists[edge.from].pushBack(edge);
    }

public:
    int addVertex(const VT& vertex) {
        int i = vertexMapping.getSize();
        vertexMapping.put(vertex, i);
        vertices.push_back(vertex);
        adjacencyLists.push_back(LinkedList<Edge>());
        return i;
    }

    void addEdge(const ET& label, const VT& from, const VT& to) {
        int f = vertexMapping.get(from);
        int t = vertexMapping.get(to);
        Edge edge(label, f, t);
        edges.push_back(label);
        adjacencyLists[f].pushBack(edge);
    }

    inline const LinkedList<Edge>& adjacentEdges(const VT& vertex) {
        return adjacencyLists[vertexMapping.get(vertex)];
    }

    void MaximFomin_bfs(const VT& start,
                        function<void(const VT& from, const VT& to, const ET& edge)> visit = [](auto){}) {
        vector<char> visited(vertices.size(), 0);
        LinkedList<helpTuple> queue;
        queue.pushBack({-1, vertexMapping.get(start), nullptr});
        while (queue.getSize()) {
            auto [from, to, edge] = *queue.begin();
            queue.remove(queue.begin());
            visited[to] = true;
            if (from != -1) {
                visit(vertices[from], vertices[to], edge->data);
            }
            for (const auto& e : adjacentEdges(vertices[to])) {
                if (visited[e.to]) {
                    continue;
                }
                queue.pushBack({e.from, e.to, &e});
            }
        }
    }

    /*
     * Summary:
     * 1. tart with any vertex in the graph.
     * 2. Progressively grow a tree by adding the least-weight edge that connects an existing vertex in the tree to
     * a vertex not yet included.
     * 3. Repeat step 2 until all vertices are incorporated into the tree.
     *
     * Time complexity:
     * Since each edge should be added to a priority queue, the total complexity is |E|*log(|E|).
     */
    Graph<VT, ET> MaximFomin_mst(function<int(const ET&)> weights = [](const ET& e){ return e; }) {
        Graph<VT, ET> msf;
        if (vertices.size() == 0) {
            return msf;
        }

        for (const auto &item: vertices) {
            msf.addVertex(item);
        }
        vector<char> visited(vertices.size(), 0);
        vector<helpTuple> initial(vertices.size());
        for (int i = 0; i < vertices.size(); i++) {
            initial[i] = {INT32_MAX, i, nullptr};
        }
        BinaryHeap<helpTuple> priorityQueue(initial, greater<>());
        while (priorityQueue.size()) {
            auto [weight, vertex, edgePointer] = priorityQueue.top();
            priorityQueue.popTop();
            if (visited[vertex]) {
                continue;
            }
            visited[vertex] = true;
            if (edgePointer != nullptr) {
                msf.addEdge1(*edgePointer);
            }
            for (const auto& u : adjacencyLists[vertex]) {
                if (!visited[u.to]) {
                    priorityQueue.put({weights(u.data), u.to, &u});
                }
            }
        }
        return msf;
    }
};

int main() {
    // I/O speed-up
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);

    Graph<int, long long> graph;
    int n;
    long long m;
    cin >> n >> m;
    for (int i = 0; i < n; i++) {
        graph.addVertex(i);
    }
    for (int i = 0; i < m; i++) {
        int x, y, w;
        cin >> x >> y >> w;
        x--; y--;
        graph.addEdge(w, x, y);
        graph.addEdge(w, y, x);
    }

    auto msf = graph.MaximFomin_mst();
    int c = 0;
    vector<pair<int, int>> firstLines;
    vector<ostringstream> outs;
    vector<char> visited(n, false);
    for (int v = 0; v < n; v++) {
        if (visited[v]) {
            continue;
        }
        visited[v] = true;
        int treeSize = 0;
        outs.emplace_back();
        msf.MaximFomin_bfs(v, [&](int f, int t, long long e) {
            visited[t] = true;
            treeSize++;
            outs[c] << f+1 << ' ' << t+1 << ' ' << e << '\n';
        });
        firstLines.emplace_back(treeSize+1, v+1);
        c++;
    }

    cout << c << '\n';
    for (int i = 0; i < c; i++) {
        cout << firstLines[i].first << ' ' << firstLines[i].second << '\n';
        cout << outs[i].str();
    }

    return 0;
}
