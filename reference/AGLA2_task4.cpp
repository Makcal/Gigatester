#include <iostream>
#include <cstring>
#include <stdexcept>
#include <iomanip>

using namespace std;

template<typename NumT>
class Matrix {
protected:
    NumT *arr;
    size_t m, n;

    void init(NumT* init_arr) {
        memcpy(arr, init_arr, m * n * sizeof(NumT));
    }

public:
    Matrix(size_t m, size_t n) : m(m), n(n) {
        arr = new NumT[m * n * sizeof(NumT)];
    }

    Matrix(size_t m, size_t n, NumT* init_arr) : Matrix(m, n) {
        init(init_arr);
    }

    Matrix(const Matrix<NumT>& other) : Matrix(m, n, other.arr) {}

    Matrix(Matrix<NumT>&& other) noexcept : m(other.m), n(other.n) {
        arr = other.arr;
        other.arr = nullptr;
    }

    virtual ~Matrix() {
        delete[] arr;
    }

    bool checkSize(const Matrix<NumT>& other) const {
        return m == other.m && n == other.n;
    }

    Matrix<NumT> transpose() const {
        Matrix<NumT> t(n+0, m);
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                t[j][i] = this->arr[i*n+j];
            }
        }
        return t;
    }

    virtual inline const NumT* operator[](int i) const {
        return arr + n*i;
    }

    Matrix<NumT>& operator=(const Matrix<NumT>& other) noexcept {
        if (this == &other) return *this;
        delete[] arr;
        m = other.m;
        n = other.n;
        arr = new NumT[m * n * sizeof(NumT)];
        init(other.arr);
        return *this;
    }

    Matrix<NumT>& operator=(Matrix<NumT>&& other) noexcept {
        m = other.m;
        n = other.n;
        arr = other.arr;
        other.arr = nullptr;
        return *this;
    }

    Matrix<NumT> operator+(const Matrix<NumT>& other) {
        if (!checkSize(other)) {
            throw domain_error("Error: the dimensional problem occurred");
        }
        Matrix<NumT> c(m, n);
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                c.arr[i*n+j] = this->arr[i*n+j] + other.arr[i*n+j];
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
                c.arr[i*n+j] = this->arr[i*n+j] - other.arr[i*n+j];
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
                    sum += this->arr[i*this->n+k] * other.arr[k*other.n+j];
                }
                c.arr[i*c.n+j] = sum;
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
                this->arr[i*n+j] = (i == j ? 1 : 0);
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
                this->arr[i*n+j] = (i == j ? 1 : 0);
            }
        }
        this->arr[to*n+from] = value;
    }
};

template<typename NumT>
class PermutationMatrix : public SquareMatrix<NumT> {
public:
    explicit PermutationMatrix(size_t n, size_t row1, size_t row2) : SquareMatrix<NumT>(n) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                this->arr[i*n+j] = (i == j ? 1 : 0);
            }
        }
        this->arr[row1*n+row1] = 0;
        this->arr[row2*n+row2] = 0;
        this->arr[row1*n+row2] = 1;
        this->arr[row2*n+row1] = 1;
    }
};

int main() {
    int an;
    cin >> an;
    SquareMatrix<double> A(an);
    cin >> A;

    cout << std::fixed << std::setprecision(2);

    double det = 1;
    int step = 1;
    for (int j = 0; j < an; j++) {
        {
            int maxi = j;
            for (int i = j+1; i < an; i++) {
                if (abs(A[i][j]) > abs(A[maxi][j])) {
                    maxi = i;
                }
            }
            if (maxi != j) {
                cout << "step #" << step++ << ": permutation\n";
                A = PermutationMatrix<double>(an, maxi, j) * A;
                cout << A << '\n';
            }
        }

        det *= A[j][j];

        for (int i = j+1; i < an; i++) {
            if (A[i][j] == 0) {
                continue;
            }
            A = EliminationMatrix<double>(an, i, j, -A[i][j] / A[j][j]) * A;
            cout << "step #" << step++ << ": elimination\n";
            cout << A << '\n';
        }
    }

    if (det == -0.0) {
        det = 0.0;
    }
    cout << "result:\n" << det << '\n';
}
