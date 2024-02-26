// Author: Maxim Fomin
#include <iostream>
#include <functional>
#include <cmath>

using namespace std;

struct Item {
    int id;
    int current_price;
    int max_price;
};

template<typename T>
T* MaximFomin_count_srt(T* begin, T* end, pair<int, int> range, function<int(const T&)> key) {
    int rangeLength = range.second - range.first + 1;
    int* sum = new int[rangeLength] {};
    T* output = new T[end - begin];
    for (auto it = begin; it != end; it++) {
        sum[key(*it) - range.first]++;
    }
    for (int i = 1; i < rangeLength; i++) {
        sum[i] += sum[i-1];
    }
    for (auto it = end-1; it >= begin; it--) {
        output[--sum[key(*it) - range.first]] = *it;
    }
    delete[] sum;
    return output;
}

template<typename T>
class AbsRadixHelper {
public:
    virtual pair<int, int> getCharRange() = 0;

    virtual int getChar(const T& obj, int i) = 0;

    virtual void nextIteration() = 0;

    virtual int getIterationCount(T* begin, T* end) = 0;

    virtual ~AbsRadixHelper() = default;
};

template<
    typename T,
    typename HelperT,
    typename enable_if<is_base_of<AbsRadixHelper<T>, HelperT>::value>::type* = nullptr
>
T* MaximFomin_radix_srt(T* begin, T* end) {
    HelperT helper;
    int len = end - begin;
    T* output = begin;
    int d = helper.getIterationCount(begin, end);
    int i = 0;
    auto key = [&i, &helper](const T& x) { return helper.getChar(x, i); };
    for (i = 0; i < d; i++) {
        T* new_array = MaximFomin_count_srt(
            output,
            output + len,
            helper.getCharRange(),
            (function<int(const T&)>) key
        );
        if (i != 0) {
            free(output);
        }
        output = new_array;
        helper.nextIteration();
    }
    return output;
}

class ItemRadixHelper : public AbsRadixHelper<Item> {
private:
    int power;
    int base;

public:
    explicit ItemRadixHelper(int base = 10) : power(1), base(base), AbsRadixHelper() {}

    pair<int, int> getCharRange() override {
        return {0, base-1};
    }

    int getChar(const Item& obj, int i) override {
        return obj.max_price / power % base;
    }

    void nextIteration() override {
        power *= base;
    }

    int getIterationCount(Item *begin, Item *end) override {
        int max_max_price = 0;
        for (auto it = begin; it != end; it++) {
            max_max_price = max(max_max_price, it->max_price);
        }
        if (max_max_price == 0) return 1;
        return (int)log10(max_max_price) + 1;
    }
};

int main() {
    // I/O speed up
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);

    int n;
    cin >> n;
    Item* arr = new Item[n];
    for (int i = 0; i < n; i++) {
        arr[i].id = i+1;
        cin >> arr[i].current_price >> arr[i].max_price;
    }

    ItemRadixHelper helper;
    arr = MaximFomin_radix_srt<Item, ItemRadixHelper>(arr, arr+n);
    arr = MaximFomin_count_srt(
        arr,
        arr+n,
        {0, 100},
        (function<int(const Item&)>)[](const Item& i) { return 100 - i.current_price; }
    );

    for (int i = 0; i < n; i++) {
        cout << arr[i].id << ' ';
    }
    cout << endl;

    delete[] arr;
}
