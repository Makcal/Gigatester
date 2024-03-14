//DmitriiKuznetsov
//This is implementation of Bentley-Ottman algorithm.
//I take the idea of finding intersections using cross-poduct from this source (https://www.geeksforgeeks.org/given-a-set-of-line-segments-find-if-any-two-segments-intersect/)
//Implementation of RB-tree almost purely from Cormen, except deletion - it slightly different(Cormen version gives errors).
#include <iostream>
#include <vector>
using namespace std;

class Point{
public:
    int x;
    int y;
    Point(){};
    Point(int x, int y){
        this->x = x;
        this->y = y;
    }
    
    
};

class Segment {
public:
    Point start;
    Point end;
    Segment(){};

    Segment(int x1, int y1, int x2, int y2) : start(x1,y1), end(x2,y2) {}

    bool operator<(const Segment& other) const {
        
        return start.x < other.start.x;
    }

    bool operator>(const Segment& other) const {
        
        return start.x > other.start.x;
    }

    bool operator<=(const Segment& other) const {
        
        return start.x <= other.start.x;
    }

    bool operator>=(const Segment& other) const {
        return start.x >= other.start.x;
    }
};

template<typename T>
void merge(vector<T>& arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    vector<T> L(n1), R(n2);
    for (int i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (int j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];
    int i = 0, j = 0, k = left;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        } else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }
    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }
    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }
}

template<typename T>
void mergeSort(vector<T>& arr, int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }
}

template<typename K, typename V>
class Node{
public:
    K key;
    V value;
    Node<K,V> * left;
    Node<K,V> *right;
    Node<K,V> * parent;
    string color;
    Node(K k, V v){
        key = k;
        value = v;
        left = nullptr;
        right = nullptr;
        parent = nullptr;
        color = "RED";
    }
};

template<typename K, typename V>
class RedBlackTree{
public:
    Node<K,V> * root;
    RedBlackTree(){
        root = nullptr;
    }

    void rotateLeft(Node<K,V>* node) {
        Node<K,V>* rightChild = node->right;
        node->right = rightChild->left;
        if (rightChild->left != nullptr) {
            rightChild->left->parent = node;
        }
        rightChild->parent = node->parent;
        if (node->parent == nullptr) {
            root = rightChild;
        } else if (node == node->parent->left) {
            node->parent->left = rightChild;
        } else {
            node->parent->right = rightChild;
        }
        rightChild->left = node;
        node->parent = rightChild;
    }


    void rotateRight( Node<K,V>* node) {
        Node<K,V> *leftChild = node->left;
        node->left = leftChild->right;
        if (leftChild->right != nullptr) {
            leftChild->right->parent = node;
        }
        leftChild->parent = node->parent;
        if (node->parent == nullptr) {
            root = leftChild;
        } else if (node == node->parent->right) {
            node->parent->right = leftChild;
        } else {
            node->parent->left = leftChild;
        }
        leftChild->right = node;
        node->parent = leftChild;

    }

    void insert(K key, V value){
        Node<K,V>* newNode = new Node<K,V>(key, value);
        if(root == nullptr){
            root = newNode;

        }
        else{
            Node<K,V> *p = root;
            Node<K,V> *q = nullptr;
            while(p != nullptr){
                q = p;
                if(p->key < newNode->key){
                    p = p->right;

                }
                else{
                    p = p->left;
                }

            }
            newNode->parent = q;

            if(q->key < newNode->key){
                q->right = newNode;
            }
            else{
                q->left = newNode;
            }

        }
        insertionFixUp(newNode);
    }
    void insertionFixUp( Node<K,V>* newNode) {
        while (newNode != root && newNode->parent->color == "RED") {
            if (newNode->parent == newNode->parent->parent->left) {
                Node<K,V>* uncle = newNode->parent->parent->right;
                if (uncle != NULL && uncle->color == "RED") {
                    newNode->parent->color = "BLACK";
                    uncle->color = "BLACK";
                    newNode->parent->parent->color = "RED";
                    newNode = newNode->parent->parent;
                } else {
                    if (newNode == newNode->parent->right) {
                        newNode = newNode->parent;
                        rotateLeft(newNode);
                    }
                    newNode->parent->color = "BLACK";
                    newNode->parent->parent->color = "RED";
                    rotateRight( newNode->parent->parent);
                }
            } else {
                Node<K,V>* uncle = newNode->parent->parent->left;
                if (uncle != NULL && uncle->color == "RED") {
                    newNode->parent->color = "BLACK";
                    uncle->color = "BLACK";
                    newNode->parent->parent->color = "RED";
                    newNode = newNode->parent->parent;
                } else {
                    if (newNode == newNode->parent->left) {
                        newNode = newNode->parent;
                        rotateRight( newNode);
                    }
                    newNode->parent->color = "BLACK";
                    newNode->parent->parent->color = "RED";
                    rotateLeft( newNode->parent->parent);
                }
            }
        }
        root->color = "BLACK";
    }

    Node<K,V> * minimum(Node<K,V> * x ){
        while(x->left != nullptr){
            x = x->left;
        }
        return x;
    }

    Node<K,V> * maximum(Node<K,V> * x ){
        while(x->right != nullptr){
            x = x->right;
        }
        return x;
    }

    void remove(K key){
        Node<K,V>* nodeToRemove = search(key);
        if(nodeToRemove == nullptr){
            return;
        }
        Node<K,V>* y;
        if(nodeToRemove->left != nullptr && nodeToRemove->right != nullptr){

            Node<K,V>* successor = minimum(nodeToRemove->right);
            nodeToRemove->key = successor->key;
            nodeToRemove->value = successor->value;
            nodeToRemove = successor;
        }

        if(nodeToRemove->left != nullptr){
            y = nodeToRemove->left;
        }
        else{
            y = nodeToRemove->right;
        }
        if(y != nullptr){

            y->parent = nodeToRemove->parent;
        }
        if(nodeToRemove->parent == nullptr){

            root = y;
        }
        else if(nodeToRemove == nodeToRemove->parent->left){
            nodeToRemove->parent->left = y;
        }
        else{
            nodeToRemove->parent->right = y;
        }
        if(nodeToRemove->color == "BLACK"){

            removeFixUp(y, nodeToRemove->parent);
        }
        delete nodeToRemove;
    }

    void removeFixUp(Node<K,V>* x, Node<K,V>* xParent){
        while(x != root && (x == nullptr || x->color == "BLACK")){
            if(x == xParent->left){
                Node<K,V>* sibling = xParent->right;
                if(sibling->color == "RED"){
                    sibling->color = "BLACK";
                    xParent->color = "RED";
                    rotateLeft(xParent);
                    sibling = xParent->right;
                }
                if((sibling->left == nullptr || sibling->left->color == "BLACK") &&
                   (sibling->right == nullptr || sibling->right->color == "BLACK")){
                    sibling->color = "RED";
                    x = xParent;
                    xParent = x->parent;
                }
                else{
                    if(sibling->right == nullptr || sibling->right->color == "BLACK"){
                        sibling->left->color = "BLACK";
                        sibling->color = "RED";
                        rotateRight(sibling);
                        sibling = xParent->right;
                    }
                    sibling->color = xParent->color;
                    xParent->color = "BLACK";
                    sibling->right->color = "BLACK";
                    rotateLeft(xParent);
                    x = root;
                }
            }
            else{
                Node<K,V>* w = xParent->left;
                if(w->color == "RED"){
                    w->color = "BLACK";
                    xParent->color = "RED";
                    rotateRight(xParent);
                    w = xParent->left;
                }
                if((w->right == nullptr || w->right->color == "BLACK") &&
                   (w->left == nullptr || w->left->color == "BLACK")){
                    w->color = "RED";
                    x = xParent;
                    xParent = x->parent;
                }
                else{
                    if(w->left == nullptr || w->left->color == "BLACK"){
                        w->right->color = "BLACK";
                        w->color = "RED";
                        rotateLeft(w);
                        w = xParent->left;
                    }
                    w->color = xParent->color;
                    xParent->color = "BLACK";
                    w->left->color = "BLACK";
                    rotateRight(xParent);
                    x = root;
                }
            }
        }
        if(x != nullptr){
            x->color = "BLACK";
        }
    }







    Node<K,V> * search(K key){
        Node<K,V> * x = root;
        while(x != nullptr and  x->key != key ){
            if(key < x->key){
                x = x->left;

            }
            else{
                x = x->right;
            }
        }
        return x;
    }
};



int crossProduct(int x1, int y1, int x2, int y2, int x3, int y3) {
    int val = (y2 - y1) * (x3 - x2) - (x2 - x1) * (y3 - y2);

    if (val == 0) return 0;
    return (val > 0) ? 1 : 2;
}

bool lieOnSegment(int x1, int y1, int x2, int y2, int x, int y) {
    return (x >= min(x1, x2) && x <= max(x1, x2) &&
            y >= min(y1, y2) && y <= max(y1, y2));
}

bool hasIntersection(const Segment& segment1, const Segment& segment2) {
    int o1 = crossProduct(segment1.start.x, segment1.start.y, segment1.end.x, segment1.end.y, segment2.start.x, segment2.start.y);
    int o2 = crossProduct(segment1.start.x, segment1.start.y, segment1.end.x, segment1.end.y, segment2.end.x, segment2.end.y);
    int o3 = crossProduct(segment2.start.x, segment2.start.y, segment2.end.x, segment2.end.y, segment1.start.x, segment1.start.y);
    int o4 = crossProduct(segment2.start.x, segment2.start.y, segment2.end.x, segment2.end.y, segment1.end.x, segment1.end.y);

    if (o1 != o2 && o3 != o4)
        return true;

    return (o1 == 0 && lieOnSegment(segment1.start.x, segment1.start.y, segment1.end.x, segment1.end.y, segment2.start.x, segment2.start.y)) ||
           (o2 == 0 && lieOnSegment(segment1.start.x, segment1.start.y, segment1.end.x, segment1.end.y, segment2.end.x, segment2.end.y)) ||
           (o3 == 0 && lieOnSegment(segment2.start.x, segment2.start.y, segment2.end.x, segment2.end.y, segment1.start.x, segment1.start.y)) ||
           (o4 == 0 && lieOnSegment(segment2.start.x, segment2.start.y, segment2.end.x, segment2.end.y, segment1.end.x, segment1.end.y));
}
template<typename K, typename V>
void traverse(Node<K,V> *node, Segment currentSegment, vector<Segment>& intersectingSegments) {
    if (!intersectingSegments.empty())
        return;
    if (node != nullptr) {
        traverse(node->left, currentSegment, intersectingSegments);

        if (hasIntersection(currentSegment, node->value)) {
            intersectingSegments.push_back(node->value);
            return;
        }


        traverse(node->right, currentSegment, intersectingSegments);
    }
}
template<typename K, typename V>
vector<Segment> getIntersections(Segment& currentSegment, RedBlackTree<K,V>& activeSegments) {
    vector<Segment> intersectingSegments;
    traverse(activeSegments.root, currentSegment, intersectingSegments);
    return intersectingSegments;
}

int main(){
    ios_base::sync_with_stdio(0);
    cin.tie(0);
    cout.tie(0);

    int n;
    cin >> n;
    vector<Segment> segments;
    for (int i = 0; i < n; i++) {
        int xP, yP, xQ, yQ;
        cin >> xP >> yP >> xQ >> yQ;
        segments.push_back(Segment(xP, yP, xQ, yQ));
    }

    mergeSort(segments,0, segments.size() - 1);
    RedBlackTree<Segment, Segment> redBlackTree = RedBlackTree<Segment, Segment>();
    for (auto& segment : segments) {
        auto intersections = getIntersections(segment, redBlackTree);
        if (!intersections.empty()) {
            cout << "INTERSECTION" << endl;
            cout << segment.start.x << " " << segment.start.y << " " << segment.end.x << " " << segment.end.y << endl;
            cout << intersections[0].start.x << " " << intersections[0].start.y << " "
                 << intersections[0].end.x << " " << intersections[0].end.y<< endl;
            return 0;
        }
        redBlackTree.insert(segment, segment);
    }

    cout << "NO INTERSECTIONS" << endl;

    return 0;
}