#include <bits/stdc++.h>

using namespace std;

vector<string>* search(string &input, vector<string> &dict, int i) {
    if (i == input.length()) {
        return new vector<string>();
    }
    for (auto &s : dict) {
        if (i + s.length() > input.length()) {
            continue;
        }
        for (int j = 0; j < s.length(); j++) {
            if (s[j] != input[i+j]) {
                goto skip;
            }
        }
        {
            auto check = search(input, dict, i + (int) s.length());
            if (check != nullptr) {
                check->push_back(s);
                return check;
            }
        }

        skip:
        ;
    }
    return nullptr;
}

int main() {
    // I/O speed up
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);

    int n, k;
    cin >> n >> k;
    vector<string> dict(n);
    for (int i = 0; i < n; i++) {
        cin >> dict[i];
    }
    sort(dict.begin(), dict.end(), [](string &s1, string &s2) { return s1.length() > s2.length(); });
    string in;
    cin >> in;

    auto res = search(in, dict, 0);
    for (int i = (int) res->size() - 1; i >= 0; i--) {
        cout << (*res)[i] << ' ';
    }
    cout << endl;
}
