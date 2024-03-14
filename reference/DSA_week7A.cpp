// Author: Maxim Fomin
#include <iostream>

using namespace std;

template <typename K>
class RedBlackTree {
    class Node {
        friend RedBlackTree;

        K value;
        bool isBlack;
        Node* left;
        Node* right;
        Node* parent;

        Node(const K& value, bool isBlack) : Node(value, isBlack, nullptr) {}

        Node(const K& value, bool isBlack, Node* parent)
            : value(value), left(nullptr), right(nullptr), parent(parent), isBlack(isBlack) {}
    };

    Node* root = nullptr;

    void rotate(Node* top, bool right) {
        Node* sub = right ? top->right : top->left;
        if (top != root) {
            bool topRight = top->parent->right == top;

            if (topRight) {
                top->parent->right = sub;
            } else {
                top->parent->left = sub;
            }
        }
        else {
            root = sub;
        }
        sub->parent = top->parent;

        if (right) {
            top->right = sub->left;
            if (sub->left != nullptr) sub->left->parent = top;
            sub->left = top;
        } else {
            top->left = sub->right;
            if (sub->right != nullptr) sub->right->parent = top;
            sub->right = top;
        }
        top->parent = sub;
    }

public:
    RedBlackTree() = default;

    void insert(const K& value) {
        if (root == nullptr) {
            root = new Node(value, true);
            return;
        }

        Node* current;
        auto next = root;
        do {
            current = next;
            if (value < current->value) {
                next = current->left;
            }
            else {
                next = current->right;
            }
        } while (next != nullptr);
        if (value >= current->value) {
            current->right = new Node(value, false, current);
        }
        else {
            current->left = new Node(value, false, current);
        }

        fix_up:
        if (current == nullptr || current->isBlack) return;

        Node* parent = current;
        Node* uncle;
        bool parentRight = (parent == parent->parent->right);
        if (parentRight) {
            uncle = parent->parent->left;
        }
        else {
            uncle = parent->parent->right;
        }

        // case 1
        if (uncle != nullptr && !uncle->isBlack) {
            uncle->isBlack = true;
            parent->isBlack = true;
            if (parent->parent != root) parent->parent->isBlack = false;

            current = current->parent->parent;
            goto fix_up;
        }

        // case 2
        bool childRight = (value >= current->value);
        Node *child = (childRight ? parent->right : parent->left);
        if (childRight == parentRight) {
            rotate(parent->parent, childRight);
            child->isBlack = true;
            if (child->parent == root) root->isBlack = true;
            current = current->parent;
            goto fix_up;
        }

        // case 3
        if (childRight != parentRight) {
            rotate(parent, childRight);
            rotate(child->parent, parentRight);
            parent->isBlack = true;
            if (child == root) {
                child->isBlack = true;
                child->left->isBlack = false;
                child->right->isBlack = false;
            }

            current = child->parent;
            goto fix_up;
        }
    }

    void iterate() {
        int i = 1;
        traverse(root, &i);
    }

    void traverse(Node* node, int* counter) {
        int l = -1, r = -1;
        if (node->left != nullptr) {
            traverse(node->left, counter);
            l = *counter - 1;
        }
        if (node->right != nullptr) {
            traverse(node->right, counter);
            r = *counter - 1;
        }
        cout << node->value << ' ' << l << ' ' << r << '\n';
        (*counter)++;
    }
};

int main() {
    // I/O speed up
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);

    int n;
    cin >> n;
    cout << n << '\n';
    RedBlackTree<int> tree;
    for (int i = 0; i  < n; i++) {
        int x;
        cin >> x;
        tree.insert(x);
    }
    tree.iterate();
    cout << n << endl;
    return 0;
}
