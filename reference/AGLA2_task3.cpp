#include <iostream>
#include <cstring>
#include <stdexcept>

using namespace std;

template<typename NumT>
class Matrix {
protected:
    NumT *arr;
    size_t m, n;

public:
    Matrix(size_t m, size_t n) : m(m), n(n) {
        arr = (NumT*)malloc(m * n * sizeof(NumT));
    }

    Matrix(const Matrix<NumT>& other) : m(other.m), n(other.n) {
        init(other.arr);
    }

    Matrix(Matrix<NumT>&& other) noexcept : m(other.m), n(other.n) {
        arr = other.arr;
        other.arr = nullptr;
    }

    virtual ~Matrix() {
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

    virtual inline const NumT* operator[](int i) const {
        return arr + n*i;
    }

    virtual inline NumT* operator[](int i) {
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

    explicit SquareMatrix(const Matrix<NumT>& m) : Matrix<NumT>(m) {}

    explicit SquareMatrix(Matrix<NumT>&& m) : Matrix<NumT>(std::move(m)) {}

    SquareMatrix<NumT> operator*(const SquareMatrix<NumT>& other) {
        return SquareMatrix<NumT>((*this).Matrix<NumT>::operator*(other));
    }
};

template<typename NumT>
class IdentityMatrix : public SquareMatrix<NumT> {
public:
    explicit IdentityMatrix(size_t n) : SquareMatrix<NumT>(n) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                (*this).SquareMatrix<NumT>::operator[](i)[j] = (i == j ? 1 : 0);
            }
        }
    }
};

template<typename NumT>
class EliminationMatrix : public SquareMatrix<NumT> {
public:
    explicit EliminationMatrix(size_t n, size_t to, size_t from, NumT value) : SquareMatrix<NumT>(n) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                (*this)[i][j] = (i == j ? 1 : 0);
            }
        }
        (*this)[to][from] = value;
    }
};

template<typename NumT>
class PermutationMatrix : public SquareMatrix<NumT> {
public:
    explicit PermutationMatrix(size_t n, size_t row1, size_t row2) : SquareMatrix<NumT>(n) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                (*this)[i][j] = (i == j ? 1 : 0);
            }
        }
        (*this)[row1][row1] = 0;
        (*this)[row2][row2] = 0;
        (*this)[row1][row2] = 1;
        (*this)[row2][row1] = 1;
    }
};

int main() {
    int an;

    cin >> an;
    SquareMatrix<int> A(an);
    cin >> A;

    cout << IdentityMatrix<int>(3) << '\n';
    EliminationMatrix<int> E21(an, 1, 0, -A[1][0]/A[0][0]);
    cout << E21 << '\n';
    SquareMatrix<int> B = E21 * A;
    cout << B << '\n';
    PermutationMatrix<int> P21(an, 1, 0);
    cout << P21 << '\n';
    SquareMatrix<int> C = P21 * A;
    cout << C << '\n';
}
