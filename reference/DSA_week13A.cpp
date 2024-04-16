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
    int _size = 0;
    ListNode<T>* sentinel;

    void removeNode(ListNode<T>* node) {
        if (node == sentinel) return;
        node->next->prev = node->prev;
        node->prev->next = node->next;
        _size--;
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
            _size++;
        }
    }

    void clear() {
        if (_size == 0) return;

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
        if (_size == 0) {
            delete sentinel;
            return;
        }
        clear();
        delete sentinel;
    }

    int size() {
        return _size;
    }

    void push_back(const T& element) {
        auto ep = new T(element);
        auto new_node = new ListNode<T>(ep);
        new_node->prev = sentinel->prev;
        new_node->next = sentinel;
        sentinel->prev->next = new_node;
        sentinel->prev = new_node;
        _size++;
    }

    void erase(const ListIterator<T> &it) {
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

//    KeyValuePair() = default;

    KeyValuePair(const K& k, const V& v) {
        key = k;
        value = v;
    }

    bool operator==(const KeyValuePair<K, V>& other) const {
        return key == other.key && value == other.value;
    }
};

/*template<typename K, typename V>
class HashMap {
private:
    template<class T>
    using list_type = LinkedList<T>;
//    using list_type = std::list<T>;

    int _size = 0;
    int table_size = 13;
    list_type<KeyValuePair<K, V>>** table;

    template<typename T>
    static int hash(T object) {
        return abs((int)std::hash<T>()(object));
    }

    static bool putIntoTable(const KeyValuePair<K, V>& pair, list_type<KeyValuePair<K, V>>** table, int table_size) {
        bool replaced = false;
        int slot = hash<K>(pair.key) % table_size;
        for (const KeyValuePair<K, V>& p : *table[slot]) {
            if (p.key == pair.key) {
                replaced = table[slot]->removeFirst(p);
                break;
            }
        }
        table[slot]->push_back(pair);
        return replaced;
    }

    void resize(int new_size) {
        auto new_table = new list_type<KeyValuePair<K, V>>*[new_size];
        for (int i = 0; i < new_size; i++) {
            new_table[i] = new list_type<KeyValuePair<K, V>>();
        }
        for (const auto& pair : *getEntrySet()) {
            putIntoTable(pair, new_table, new_size);
        }

        freeTable(table, table_size);
        table = new_table;
        table_size = new_size;
    }

    void freeTable(list_type<KeyValuePair<K, V>>** table_p, int size) {
        for (int i = 0; i < size; i++) {
            delete table_p[i];
        }
        delete[] table_p;
    }

public:
    HashMap() {
        table = new list_type<KeyValuePair<K, V>>*[table_size];
        for (int i = 0; i < table_size; i++) {
            table[i] = new list_type<KeyValuePair<K, V>>();
        }
    }

    ~HashMap() {
        freeTable(table, table_size);
    }

    int size() {
        return _size;
    }

    void put(const K& key, const V& value) {
        if (_size >= 8 * table_size) {
            resize(table_size + 10);
        }
        if (!putIntoTable(KeyValuePair<K, V>(key, value), table, table_size))
            _size++;
    }

    void insert(const pair<K, V>& pair) {
        put(pair.first, pair.second);
    }

    V& get(const K& key) {
        int slot = hash<K>(key) % table_size;
        for (KeyValuePair<K, V>& p : *table[slot]) {
            if (p.key == key) {
                return p.value;
            }
        }
        throw runtime_error("No such key");
    }

    bool hasKey(const K& key) {
        int slot = hash<K>(key) % table_size;
        for (const KeyValuePair<K, V>& p : *table[slot]) {
            if (p.key == key) {
                return true;
            }
        }
        return false;
    }

    list_type<KeyValuePair<K, V>>* getEntrySet() {
        auto list = new list_type<KeyValuePair<K, V>>();

        for (int i = 0; i < table_size; i++) {
            for (const auto& pair : *table[i]) {
                list->push_back(pair);
            }
        }

        return list;
    }

    V& operator[](const K& key) {
        if (hasKey(key)) {
            return get(key);
        }
        put(key, V());
        return get(key);
    }
}; */

// Open Addressing
template<typename K, typename V>
class HashMap {
private:
    int _size = 0;
    int table_size = 13;
    KeyValuePair<K, V>** table;

    template<typename T>
    static int hash(const T& object) {
        return abs((int)std::hash<T>()(object));
    }

    template<typename T>
    static int getSlot(const T& key, int i, int table_size) {
        return (hash<K>(key) + i*i) % table_size;
    }

    static bool putIntoTable(const KeyValuePair<K, V>& pair, KeyValuePair<K, V>** table, int table_size) {
        for (int i = 0; i < table_size; i++) {
            int slot = getSlot(pair.key, i, table_size);
            if (table[slot] == nullptr) {
                table[slot] = new KeyValuePair<K, V>(pair);
                return false;
            }
            if (table[slot]->key == pair.key) {
                table[slot]->value = pair.value;
                return true;
            }
        }
        throw runtime_error("The table is full");
    }

    void resize(int new_size) {
        auto new_table = new KeyValuePair<K, V>*[new_size]{};
        for (int i = 0; i < table_size; i++) {
            if (table[i] != nullptr) {
                putIntoTable(*table[i], new_table, new_size);
            }
        }

        freeTable(table, table_size);
        table = new_table;
        table_size = new_size;
    }

    void freeTable(KeyValuePair<K, V>** table_p, int size) {
        for (int i = 0; i < size; i++) {
            delete table_p[i];
        }
        delete[] table_p;
    }

public:
    HashMap() {
        table = new KeyValuePair<K, V>*[table_size]{};
    }

    ~HashMap() {
        freeTable(table, table_size);
    }

    int size() {
        return _size;
    }

    void put(const K& key, const V& value) {
        if (3 * _size >= table_size) {
            resize(table_size * 5);
        }
        if (!putIntoTable(KeyValuePair<K, V>(key, value), table, table_size))
            _size++;
    }

    void insert(const pair<K, V>& pair) {
        put(pair.first, pair.second);
    }

    [[nodiscard]] V& get(const K& key) {
        for (int i = 0; i < table_size; i++) {
            int slot = getSlot(key, i, table_size);
            if (table[slot] == nullptr) {
                throw runtime_error("No such key");
            }
            if (table[slot]->key == key) {
                return table[slot]->value;
            }
        }
        throw runtime_error("No such key");
    }

    [[nodiscard]] const V& get(const K& key) const {
        for (int i = 0; i < table_size; i++) {
            int slot = getSlot(key, i, table_size);
            if (table[slot] == nullptr) {
                throw runtime_error("No such key");
            }
            if (table[slot]->key == key) {
                return table[slot]->value;
            }
        }
        throw runtime_error("No such key");
    }

    [[nodiscard]] bool hasKey(const K& key) const {
        for (int i = 0; i < table_size; i++) {
            int slot = getSlot(key, i, table_size);
            if (table[slot] == nullptr) {
                return false;
            }
            if (table[slot]->key == key) {
                return true;
            }
        }
        return false;
    }

    V& operator[](const K& key) {
        if (hasKey(key)) {
            return get(key);
        }
        put(key, V());
        return get(key);
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
        Graph<VT, ET>* graph;

        Edge(ET data, int from, int to, Graph<VT, ET>* graph)
                : data(std::move(data)), from(from), to(to), graph(graph) {}

    public:
        ET data;

        friend Graph;

        [[nodiscard]] VT getFrom() const {
            return graph->vertices[from];
        }

        [[nodiscard]] VT getTo() const {
            return graph->vertices[to];
        }

        bool operator==(const Edge& other) {
            return from == other.from && to == other.to;
        }
    };

private:
    template<class T>
    using list_type = LinkedList<T>;
    template<class K, class V>
    using hashmap_type = HashMap<K, V>;
//    using hashmap_type = std::unordered_map<K, V>;

    hashmap_type<VT, int> vertexMapping;
    vector<VT> vertices;
    vector<Edge> edges;
    vector<list_type<Edge>> adjacencyLists;

    /*
     * minimal_edge_weight, vertex_index, parent
     */
    using helpTuple = tuple<int, int, const Edge*>;

    void addEdge(const Edge& edge) {
        edges.push_back(edge);
        adjacencyLists[edge.from].push_back(edge);
    }

public:
    [[nodiscard]] inline int verticesCount() const {
        return vertices.size();
    }

    [[nodiscard]] const vector<VT>& getVertices() const {
        return vertices;
    }

    [[nodiscard]] const vector<Edge>& getEdges() const {
        return edges;
    }

    int addVertex(const VT& vertex) {
        int i = vertexMapping.size();
        vertexMapping.insert({vertex, i});
        vertices.push_back(vertex);
        adjacencyLists.push_back(list_type<Edge>());
        return i;
    }

    int addVertex(VT&& vertex) {
        int i = vertexMapping.size();
        vertexMapping.insert({vertex, i});
        vertices.push_back(std::move(vertex));
        adjacencyLists.push_back(list_type<Edge>());
        return i;
    }

    void addEdge(const ET& label, const VT& from, const VT& to) {
        int f = vertexMapping[from];
        int t = vertexMapping[to];
        Edge edge(label, f, t, this);
        edges.push_back(edge);
        adjacencyLists[f].push_back(edge);
    }

    inline const list_type<Edge>& adjacentEdges(const VT& vertex) {
        return adjacencyLists[vertexMapping[vertex]];
    }

    void breadthFirstSearch(const VT& start,
             function<void(const VT& from, const VT& to, const ET& edge)> visit = [](auto) {}) {
        vector<char> visited(vertices.size(), 0);
        list_type<helpTuple> queue;
        queue.push_back({-1, vertexMapping[start], nullptr});
        while (queue.size()) {
            auto [from, to, edge] = *queue.begin();
            queue.erase(queue.begin());
            visited[to] = true;
            if (from != -1) {
                visit(vertices[from], vertices[to], edge->data);
            }
            for (const auto& e : adjacentEdges(vertices[to])) {
                if (visited[e.to]) {
                    continue;
                }
                queue.push_back({e.from, e.to, &e});
            }
        }
    }

    /*
     * Summary:
     * 1. Start with any vertex in the graph.
     * 2. Progressively grow a tree by adding the least-weight edge that connects an existing vertex in the tree to
     * a vertex not yet included.
     * 3. Repeat step 2 until all vertices are incorporated into the tree.
     *
     * Time complexity:
     * Since each edge should be added to a priority queue, the total complexity is |E|*log(|E|).
     */
    template<typename WT = int>
    Graph<VT, ET> minimalSpanningForest(
            function<WT(const VT&, const VT&, const ET&)> weights = [](const VT&, const VT&, const ET& e) { return e; }
    ) {
        Graph<VT, ET> msf;
        if (vertices.size() == 0) {
            return msf;
        }

        for (const auto &item: vertices) {
            msf.addVertex(item);
        }
        vector<char> visited(vertices.size(), 0);
        vector<tuple<WT, int, const Edge*>> initial(vertices.size());
        for (int i = 0; i < vertices.size(); i++) {
            initial[i] = {INT32_MAX, i, nullptr};
        }
        BinaryHeap<tuple<WT, int, const Edge*>> priorityQueue(initial, greater<>());
        while (priorityQueue.size()) {
            auto [weight, vertex, edgePointer] = priorityQueue.top();
            priorityQueue.popTop();
            if (visited[vertex]) {
                continue;
            }
            visited[vertex] = true;
            if (edgePointer != nullptr) {
                msf.addEdge(*edgePointer);
            }
            for (const auto& u : adjacencyLists[vertex]) {
                if (!visited[u.to]) {
                    priorityQueue.put({weights(vertices[u.from], vertices[u.to], u.data), u.to, &u});
                }
            }
        }
        return msf;
    }

    /*
     * Returns a map of vertices to a pair of integers: the first integer is the distance from the start vertex to the
     * vertex, the second integer is the index of the parent vertex in a shortest path.
     */
    unordered_map<VT, pair<int, VT>> MaximFomin_sp(
            const VT& start,
            function<int(const ET&)> weights = [](const ET& e) { return e; }
    ) const {
        vector<pair<long long, int>> distances(vertices.size());
        for (int i = 0; i < vertices.size(); i++) {
            distances[i] = {INT32_MAX, -1};
        }
        int s = vertexMapping.get(start);
        distances[s] = {0, -1};
        for (int i = 0; i < vertices.size(); i++) {
            for (const auto& edge : edges) {
                if (distances[edge.to].first > distances[edge.from].first + weights(edge.data)) {
                    distances[edge.to] = {distances[edge.from].first + weights(edge.data), edge.from};
                }
            }
        }
        unordered_map<VT, pair<int, VT>> result;
        for (int i = 0; i < vertices.size(); i++) {
            result[vertices[i]] = make_pair(
                    distances[i].first,
                    distances[i].second != -1 ? vertices[distances[i].second] : vertices[i]
            );
        }
        return result;
    }
};

int main() {
    // I/O speed-up
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);

    Graph<int, long long> graph;
    int n;
    cin >> n;
    for (int i = 0; i < n; i++) {
        graph.addVertex(i);
    }
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            int w;
            cin >> w;
            if (w == 100000)
                continue;
            graph.addEdge(w, i, j);
        }
    }

    auto distances = graph.MaximFomin_sp(0);
    for (const auto& item : graph.getEdges()) {
        if (distances[item.getTo()].first > distances[item.getFrom()].first + item.data) {
            int current = distances[item.getFrom()].second;
            vector<char> visited(n, 0);
            visited[current] = 1;
            // traversing backwards to find a negative cycle
            while (!visited[current = distances[current].second]) {
                visited[current] = 1;
            }

            vector<int> cycle;
            int start = current;
            cycle.push_back(start);
            current = distances[current].second;
            while (start != current) {
                cycle.push_back(current);
                current = distances[current].second;
            }

            cout << "YES\n" << cycle.size() << '\n';
            for (auto it = cycle.rbegin(); it != cycle.rend(); it++) {
                cout << *it + 1 << ' ';
            }
            cout << '\n';
            return 0;
        }
    }
    cout << "NO\n";

    return 0;
}
