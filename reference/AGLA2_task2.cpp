#include <iostream>
#include <cstring>
#include <stdexcept>

using namespace std;

template<typename NumT>
class Matrix {
    NumT *arr;
    size_t m, n;

public:
    Matrix(size_t m, size_t n) : m(m), n(n) {
        arr = (NumT*)malloc(m * n * sizeof(NumT));
    }

    Matrix(Matrix<NumT>&& other) noexcept : m(other.m), n(other.n) {
        arr = other.arr;
        other.arr = nullptr;
    }

    ~Matrix() {
        delete arr;
    }

    void init(NumT* init_arr) {
        memcpy(arr, init_arr, m * n * sizeof(NumT));
    }

    bool checkSize(const Matrix<NumT>& other) const {
        return m == other.m && n == other.n;
    }

    Matrix<NumT> transpose() const {
        Matrix<NumT> t(n+0, m);
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                t[j][i] = (*this)[i][j];
            }
        }
        return t;
    }

    inline NumT* operator[](int i) const {
        return arr + n*i;
    }

    Matrix<NumT>& operator=(const Matrix<NumT>& other) {
        if (!checkSize(other)) {
            throw domain_error("Error: the dimensional problem occurred");
        }
        if (this == &other) return *this;
        memcpy(arr, other.arr, m * n * sizeof(NumT));
        return *this;
    }

    Matrix<NumT>& operator=(Matrix<NumT>&& other) = delete;

    Matrix<NumT> operator+(const Matrix<NumT>& other) {
        if (!checkSize(other)) {
            throw domain_error("Error: the dimensional problem occurred");
        }
        Matrix<NumT> c(m, n);
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                c[i][j] = (*this)[i][j] + other[i][j];
            }
        }
        return c;
    }

    Matrix<NumT> operator-(const Matrix<NumT>& other) {
        if (!checkSize(other)) {
            throw domain_error("Error: the dimensional problem occurred");
        }
        Matrix<NumT> c(m, n);
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                c[i][j] = (*this)[i][j] - other[i][j];
            }
        }
        return c;
    }

    Matrix<NumT> operator*(const Matrix<NumT>& other) {
        if (n != other.m) {
            throw domain_error("Error: the dimensional problem occurred");
        }
        Matrix<NumT> c(m, other.n);
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < other.n; j++) {
                NumT sum = 0;
                for (int k = 0; k < n; k++) {
                    sum += (*this)[i][k] * other[k][j];
                }
                c[i][j] = sum;
            }
        }
        return c;
    }

    friend ostream& operator<<(ostream &os, const Matrix<NumT> &matrix) {
        os << matrix[0][0];
        for (int j = 1; j < matrix.n; j++) {
            os << ' ' << matrix[0][j];
        }
        for (int i = 1; i < matrix.m; i++) {
            os << endl;
            os << matrix[i][0];
            for (int j = 1; j < matrix.n; j++) {
                os << ' ' << matrix[i][j];
            }
        }
        return os;
    }

    friend istream& operator>>(istream &is, const Matrix<NumT> &matrix) {
        for (int i = 0; i < matrix.m; i++) {
            for (int j = 0; j < matrix.n; j++) {
                is >> matrix.arr[i * matrix.n + j];
            }
        }
        return is;
    }
};

template<typename NumT>
class SquareMatrix : public Matrix<NumT> {
public:
    explicit SquareMatrix(size_t n) : Matrix<NumT>(n, n) {}
};

int main() {
    int an, bn, cn;

    cin >> an;
    SquareMatrix<int> a(an);
    cin >> a;

    cin >> bn;
    SquareMatrix<int> b(bn);
    cin >> b;

    cin >> cn;
    SquareMatrix<int> c(cn);
    cin >> c;

    try {
        cout << a + b << '\n';
    } catch (domain_error& error) {
        cout << error.what() << '\n';
    }

    try {
        cout << b - a << '\n';
    } catch (domain_error& error) {
        cout << error.what() << '\n';
    }

    try {
        cout << c * a << '\n';
    } catch (domain_error& error) {
        cout << error.what() << '\n';
    }

    try {
        cout << a.transpose() << '\n';
    } catch (domain_error& error) {
        cout << error.what() << '\n';
    }
}
