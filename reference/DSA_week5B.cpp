#include <bits/stdc++.h>

using namespace std;

int m[1000+1][10000+1];

int main() {
    // I/O speed up
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);

    int n, W;
    cin >> n >> W;
    int w[n], c[n];
    for (int i = 0; i < n; i++) {
        cin >> w[i];
    }
    for (int i = 0; i < n; i++) {
        cin >> c[i];
    }

    for (int i = 0; i <= W; i++) m[0][i] = 0;
    for (int i = 1; i <= n; i++) {
        for (int j = 0; j <= W; j++) {
            if (w[i-1] > j) {
                m[i][j] = m[i-1][j];
            }
            else {
                m[i][j] = max(m[i-1][j], m[i-1][j-w[i-1]] + c[i-1]);
            }
        }
    }

    vector<int> ans;
    int cw = W;
    for (int i = n; i > 0; i--) {
        if (m[i][cw] != m[i - 1][cw]) {
            ans.push_back(i);
            cw -= w[i - 1];
        }
    }

    cout << ans.size() << '\n';
    for (int i = (int)ans.size() - 1; i >= 0; i--) {
        cout << ans[i] << ' ';
    }
    cout << endl;
}
