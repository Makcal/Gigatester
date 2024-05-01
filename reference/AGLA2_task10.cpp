#include <iostream>
#include <cstring>
#include <cmath>
#include <vector>
#include <iomanip>

using namespace std;

template<typename NumT>
class Matrix {
protected:
    NumT *arr = nullptr;

    void init(NumT* init_arr) {
        memcpy(arr, init_arr, m * n * sizeof(NumT));
    }

public:
    size_t m, n;

    Matrix(size_t m, size_t n) : m(m), n(n), arr(new NumT[m * n * sizeof(NumT)] {}) { }

    Matrix(size_t m, size_t n, NumT* init_arr) : Matrix(m, n) {
        init(init_arr);
    }

    Matrix(const Matrix<NumT>& other) : Matrix(other.m, other.n, other.arr) { }

    Matrix(Matrix<NumT>&& other) noexcept : m(other.m), n(other.n), arr(other.arr) {
        other.arr = nullptr;
    }

    virtual ~Matrix() {
        delete[] arr;
    }

    [[nodiscard]] bool checkSize(const Matrix<NumT>& other) const {
        return m == other.m && n == other.n;
    }

    [[nodiscard]] Matrix<NumT> transpose() const {
        Matrix<NumT> t(n, m);
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                t.arr[j*m + i] = this->arr[i*n+j];
            }
        }
        return std::move(t);
    }

    [[nodiscard]] NumT abs() const {
        NumT sum = 0;
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                NumT x = (*this)[i][j];
                sum += x*x;
            }
        }
        return sqrt(sum);
    }

    virtual inline NumT* operator[](size_t i) {
        return arr + n*i;
    }

    virtual inline const NumT* operator[](size_t i) const {
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
        return std::move(c);
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
        return std::move(c);
    }

    virtual Matrix<NumT> operator*(const Matrix<NumT>& other) {
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
        return std::move(c);
    }

    friend ostream& operator<<(ostream &os, const Matrix<NumT> &matrix) {
        for (int j = 0; j < matrix.n; j++) {
            if (std::abs(matrix[0][j]) < 0.00005) matrix.arr[0*matrix.n + j] = 0;
            os << matrix[0][j] << ' ';
        }
        for (int i = 1; i < matrix.m; i++) {
            os << endl;
            for (int j = 0; j < matrix.n; j++) {
                if (std::abs(matrix[i][j]) < 0.00005) matrix.arr[i*matrix.n + j] = 0;
                os << matrix[i][j] << ' ';
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
class PermutationMatrix;

template<typename NumT>
class EliminationMatrix;

template<typename NumT>
class SquareMatrix : public Matrix<NumT> {
public:
    explicit SquareMatrix(size_t n) : Matrix<NumT>(n, n) {}

    SquareMatrix(size_t n, NumT* init_arr) : Matrix<NumT>(n, n, init_arr) {}

    explicit SquareMatrix(const Matrix<NumT>& m) : Matrix<NumT>(m) {}

    explicit SquareMatrix(Matrix<NumT>&& m) : Matrix<NumT>(std::move(m)) {}

    NumT getDeterminant();

    SquareMatrix inverse();

    virtual SquareMatrix<NumT> operator*(const SquareMatrix<NumT>& rhs) {
        this->Matrix<NumT>::operator*(rhs);
        return SquareMatrix<NumT>((*this).Matrix<NumT>::operator*(rhs));
    }

    Matrix<NumT> operator*(const Matrix<NumT>& rhs) override {
        this->Matrix<NumT>::operator*(rhs);
        return (*this).Matrix<NumT>::operator*(rhs);
    }

    bool checkDiagonalPredominance() {
        const size_t n = this->n;
        for (size_t i = 0; i < n; i++) {
            NumT d = std::abs((*this)[i][i]);
            NumT sum = 0;
            for (size_t j = 0; j < n; j++) {
                if (j == i) continue;
                sum += std::abs((*this)[i][j]);
            }
            if (d <= sum) {
                return false;
            }
        }
        return true;
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

template<typename NumT>
NumT SquareMatrix<NumT>::getDeterminant() {
    SquareMatrix temp(*this);
    size_t n = this->n;
    double det = 1;

    for (size_t j = 0; j < n; j++) {
        {
            size_t maxi = j;
            for (size_t i = j+1; i < n; i++) {
                if (abs(temp[i][j]) > abs(temp[maxi][j])) {
                    maxi = i;
                }
            }
            if (maxi != j) {
                temp = PermutationMatrix<NumT>(n, maxi, j) * temp;
                det *= -1;
            }
        }

        det *= temp[j][j];
        if (det == 0) {
            return 0;
        }

        for (size_t i = j+1; i < n; i++) {
            if (temp[i][j] == 0) {
                continue;
            }
            temp = EliminationMatrix<NumT>(n, i, j, -temp[i][j] / temp[j][j]) * temp;
        }
    }

    return det;
}

template<typename NumT>
SquareMatrix<NumT> SquareMatrix<NumT>::inverse() {
    size_t n = this->n;

    NumT* temp = new NumT[n * 2*n];
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            temp[i * 2*n + j] = (*this)[i][j];
            temp[i * 2*n + n+j] = (i == j ? 1 : 0);
        }
    }
    Matrix<NumT> AI(n, 2*n, temp);
    delete[] temp;

    if (getDeterminant() == 0) {
        throw domain_error("Error: matrix A is singular");
    }

    for (int j = 0; j < n; j++) {
        {
            int maxi = j;
            for (int i = j+1; i < n; i++) {
                if (abs(AI[i][j]) > abs(AI[maxi][j])) {
                    maxi = i;
                }
            }
            if (maxi != j) {
                AI = PermutationMatrix<NumT>(n, maxi, j) * AI;
            }
        }

        for (int i = j+1; i < n; i++) {
            if (AI[i][j] == 0) {
                continue;
            }
            AI = EliminationMatrix<NumT>(n, i, j, -AI[i][j] / AI[j][j]) * AI;
        }
    }
    // back substitution
    for (int j = (int)n-1; j >= 0; j--) {
        for (int i = j-1; i >= 0; i--) {
            if (AI[i][j] == 0) {
                continue;
            }
            AI = EliminationMatrix<NumT>(n, i, j, -AI[i][j] / AI[j][j]) * AI;
        }
    }

    for (int i = 0; i < n; i++) {
        AI = EliminationMatrix<NumT>(n, i, i, 1/AI[i][i]) * AI;
    }

    temp = new NumT[n * n];
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            temp[i*n + j] = AI[i][n+j];
        }
    }
    SquareMatrix<NumT> out(n, temp);
    delete[] temp;
    return std::move(out);
}


class PredatorPreyModel {
    double v0, k0, a1, b1, a2, b2;

    using data = pair<double, double>;

public:
    PredatorPreyModel(double v0, double k0, double a1, double b1, double a2, double b2)
            : v0(v0 - a2/b2), k0(k0 - a1/b1), a1(a1), b1(b1), a2(a2), b2(b2) {}

    [[nodiscard]] inline data atTime(double t) const {
        double root = std::sqrt(a1*a2);
        double v = v0*cos(root*t) - k0*(std::sqrt(a2)*b1)/(b2*std::sqrt(a1))*sin(root*t);
        double k = v0*(std::sqrt(a1)*b2)/(b1*std::sqrt(a2))*sin(root*t) + k0*cos(root*t);
        return {v + a2/b2, k + a1/b1};
    }
};


int main() {
    cout << std::fixed << std::setprecision(2);

    double v0, k0;
    double a1, b1, a2, b2;
    double T, N;
    cin >> v0 >> k0 >> a1 >> b1 >> a2 >> b2 >> T >> N;
    PredatorPreyModel pp(v0, k0, a1, b1, a2, b2);

    cout << "t: ";
    double step = T/N;
    for (int i = 0; i <= N; i++) {
        double t = T/N * i;
        cout << t << ' ';
    }
    cout << '\n';

    vector<pair<double, double>> v;
    for (int i = 0; i <= N; i++) {
        double t = T/N * i;
        v.push_back(pp.atTime(t));
    }

    cout << "v: ";
    for (const auto& p: v) {
        cout << p.first << ' ';
    }
    cout << '\n';

    cout << "k: ";
    for (const auto& p: v) {
        cout << p.second << ' ';
    }
    cout << '\n';
}
