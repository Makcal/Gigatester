#include <iostream>
#include <memory>
#include <utility>
#include <unordered_map>
#include <vector>
#include <algorithm>

using namespace std;

/*
 * A base class for all app exceptions.
 */
class CustomException : public std::exception {
private:
    /*
     * A message that describes the exception. Usually, fixed in a derived class's contructor.
     */
    string message;

public:
    explicit CustomException(string message) : message(std::move(message)), std::exception() {}

    // Getters

    [[nodiscard]] const string& getMessage() const {
        return message;
    }
};


/*
 * An exception that is thrown when attempting to create an already existing book.
 */
class BookExistsException : public CustomException {
public:
    explicit BookExistsException() : CustomException("Book already exists") {}
};


/*
 * An exception that is thrown when attempting to create an already existing user.
 */
class UserExistsException : public CustomException {
public:
    explicit UserExistsException() : CustomException("User already exists") {}
};


class User {
public:
    /*
     * An enum that represents the type of user.
     */
    enum Type {
        Standard,
        Premium,
    };

private:
    string username;
    Type type;
    bool _isSubscribed = false;

public:
    User(string username, Type type) : username(std::move(username)), type(type) {}

    // Getters and setters

    [[nodiscard]] const string& getUsername() const {
        return username;
    }

    [[nodiscard]] Type getType() const {
        return type;
    }

    [[nodiscard]] bool isSubscribed() const {
        return _isSubscribed;
    }

    void setIsSubscribed(bool isSubscribed) {
        _isSubscribed = isSubscribed;
    }
};


/*
 * A class that represents an author of a book. Used to share author objects between books.
 */
class Author {
private:
    string name;

    // may add some extra data

public:
    explicit Author(string name) : name(std::move(name)) {}

    // Getter

    [[nodiscard]] const string& getName() const {
        return name;
    }
};


/*
 * An interface for a book.
 */
class Book {
public:
    using PriceType = string;

    [[nodiscard]] virtual const string& getTitle() const = 0;

    [[nodiscard]] virtual const Author& getAuthor() const = 0;

    [[nodiscard]] virtual Book::PriceType getPrice() const = 0;

    virtual void setPrice(const Book::PriceType& price) = 0;

    virtual ~Book() = default;
};


/*
 * A class that represents a book. It is an implementation of a flyweight object.
 */
class FlyweightBook : public Book {
private:
    string title;
    shared_ptr<Author> author; // shared field
    Book::PriceType price;

    friend class FlyweightBookFactory;

    /*
     * A private constructor that is used by the factory to create a book.
     */
    FlyweightBook(Book::PriceType title, shared_ptr<Author> author, string price)
            : title(std::move(title)), author(std::move(author)), price(std::move(price)) {}

public:
    // Getters and setters

    [[nodiscard]] const string& getTitle() const override {
        return title;
    }

    [[nodiscard]] const Author& getAuthor() const override {
        return *author;
    }

    [[nodiscard]] Book::PriceType getPrice() const override {
        return price;
    }

    void setPrice(const Book::PriceType& newPrice) override {
        this->price = newPrice;
    }
};


/*
 * An interface for a book factory.
 */
class BookFactory {
public:
    virtual shared_ptr<Book> createBook(
            const string& title, const string& authorName, const Book::PriceType& price
    ) = 0;

    virtual ~BookFactory() = default;
};


/*
 * Singleton.
 */
class FlyweightBookFactory : public BookFactory {
private:
    /*
     * The cache. It stores authors to share them between books.
     */
    unordered_map<string, shared_ptr<Author>> authors;

    FlyweightBookFactory() = default;

public:
    /*
     * The singleton instance.
     */
    static const shared_ptr<FlyweightBookFactory> instance;

    shared_ptr<Book> createBook(
            const string& title, const string& authorName, const Book::PriceType& price
    ) override {
        if (authors.find(authorName) == authors.end()) {
            authors[authorName] = make_shared<Author>(authorName);
        }

        return make_shared<FlyweightBook>(FlyweightBook(title, authors[authorName], price));
    }
};

const shared_ptr<FlyweightBookFactory> FlyweightBookFactory::instance =
        make_shared<FlyweightBookFactory>(FlyweightBookFactory());


/*
 * An interface for an observer.
 */
template<typename EventT>
class Observer {
public:
    virtual void update(const EventT& event) = 0;

    virtual ~Observer() = default;

    virtual bool operator==(const Observer& rhs) {
        return false;
    }

    virtual bool operator!=(const Observer& rhs) {
        return !(*this == rhs);
    }
};


struct PriceUpdateEvent {
    shared_ptr<Book> book;
    Book::PriceType newPrice;
};


/*
 * An observer implementation that prints price updates.
 */
class PrintSubscriber : public Observer<PriceUpdateEvent> {
private:
    shared_ptr<User> user;

public:
    explicit PrintSubscriber(shared_ptr<User> user) : user(std::move(user)) {}

    void update(const PriceUpdateEvent& event) override {
        cout << user->getUsername() << " notified about price update for "
             << event.book->getTitle() << " to " << event.newPrice << '\n';
    }
};


/*
 * The main class of the app. It stores books and users, and notifies subscribers about price updates.
 */
class BookStore {
private:
    unordered_map<string, shared_ptr<Book>> books;
    unordered_map<string, shared_ptr<User>> users;
    vector<shared_ptr<Observer<PriceUpdateEvent>>> subscribers;

public:
    void addBook(const shared_ptr<Book> &book) {
        if (books.find(book->getTitle()) != books.end()) {
            throw BookExistsException();
        }
        books[book->getTitle()] = book;
    }

    void createUser(const shared_ptr<User> &user) {
        if (users.find(user->getUsername()) != users.end()) {
            throw UserExistsException();
        }
        users[user->getUsername()] = user;
    }

    void subscribe(const shared_ptr<Observer<PriceUpdateEvent>> &subscriber) {
        subscribers.push_back(subscriber);
    }

    void unsubscribe(const shared_ptr<Observer<PriceUpdateEvent>> &subscriber) {
        auto it = std::find(subscribers.begin(), subscribers.end(), subscriber);
        if (it == subscribers.end()) {
            return;
        }
        subscribers.erase(it);
    }

    void updatePrice(const shared_ptr<Book> &book, Book::PriceType newPrice) const {
        if (books.find(book->getTitle()) == books.end()) {
            return;
        }

        book->setPrice(newPrice);
        PriceUpdateEvent event{book, std::move(newPrice)};
        for (const auto &subscriber: subscribers) {
            subscriber->update(event);
        }
    }

    [[nodiscard]] shared_ptr<Book> getBook(const string &title) const {
        return books.at(title);
    }

    [[nodiscard]] shared_ptr<User> getUser(const string &username) const {
        auto it = users.find(username);
        return it != users.end() ? it->second : nullptr;
    }
};


/*
 * A facade for the app. It provides a simple interface for the user.
 */
class StoreFacade {
private:
    unique_ptr<BookStore> store;
    unordered_map<string, shared_ptr<PrintSubscriber>> userSubscribes;

public:
    explicit StoreFacade(unique_ptr<BookStore> store) : store(std::move(store)) {}

    bool createBook(const string& title, const string& authorName, const Book::PriceType& price) {
        auto book = FlyweightBookFactory::instance->createBook(title, authorName, price);
        try {
            store->addBook(book);
        } catch (BookExistsException&) {
            return false;
        }
        return true;
    }

    bool createUser(const string& username, User::Type type) {
        auto user = make_shared<User>(username, type);
        try {
            store->createUser(user);
        } catch (UserExistsException&) {
            return false;
        }
        return true;
    }

    bool subscribe(const string& username) {
        auto user = store->getUser(username);
        if (user->isSubscribed()) {
            return false;
        }
        user->setIsSubscribed(true);
        auto sub = make_shared<PrintSubscriber>(user);
        store->subscribe(sub);
        userSubscribes[username] = sub;
        return true;
    }

    bool unsubscribe(const string& username) {
        auto user = store->getUser(username);
        if (!user->isSubscribed()) {
            return false;
        }
        user->setIsSubscribed(false);
        store->unsubscribe(userSubscribes[username]);
        userSubscribes.erase(username);
        return true;
    }

    void updatePrice(const string& title, const Book::PriceType& newPrice) {
        auto book = store->getBook(title);
        store->updatePrice(book, newPrice);
    }

    void readBook(const string& username, const string& title) {
        auto user = store->getUser(username);
        auto book = store->getBook(title);
        cout << user->getUsername() << " reading " << book->getTitle() << " by " << book->getAuthor().getName() << '\n';
    }

    bool listenBook(const string& username, const string& title) {
        auto user = store->getUser(username);
        auto book = store->getBook(title);
        if (user->getType() == User::Type::Standard) {
            return false;
        }
        cout << user->getUsername() << " listening " << book->getTitle();
        cout << " by " << book->getAuthor().getName() << '\n';
        return true;
    }
};


/*
 * Input/output handler.
 */
class Program {
private:
    unique_ptr<StoreFacade> facade;

public:
    Program() : facade(make_unique<StoreFacade>(make_unique<BookStore>())) {}

    void run() {
        string command;
        while (cin >> command) {
            if (command == "createBook") {
                string title, author, price;
                cin >> title >> author >> price;
                if (!facade->createBook(title, author, price)) {
                    cout << "Book already exists\n";
                }
            } else if (command == "createUser") {
                string type, username;
                cin >> type >> username;
                if (
                    !facade->createUser(username,
                                        type == "standard" ? User::Type::Standard : User::Type::Premium)
                ) {
                    cout << "User already exists\n";
                }
            } else if (command == "subscribe") {
                string username;
                cin >> username;
                if (!facade->subscribe(username)) {
                    cout << "User already subscribed\n";
                }
            } else if (command == "unsubscribe") {
                string username;
                cin >> username;
                if (!facade->unsubscribe(username)) {
                    cout << "User is not subscribed\n";
                }
            } else if (command == "updatePrice") {
                string title, newPrice;
                cin >> title >> newPrice;
                facade->updatePrice(title, newPrice);
            } else if (command == "readBook") {
                string username, title;
                cin >> username >> title;
                facade->readBook(username, title);
            } else if (command == "listenBook") {
                string username, title;
                cin >> username >> title;
                if (!facade->listenBook(username, title)) {
                    cout << "No access\n";
                }
            } else if (command == "end") {
                break;
            }
        }
    }
};


/*
 * 0 memory leaks!
 */
int main() {
    Program program;
    program.run();
    return 0;
}
