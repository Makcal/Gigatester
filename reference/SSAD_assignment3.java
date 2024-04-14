import java.util.*;


public class Main {
    public static void main(String[] args) {
        // Set the locale to ensure consistent decimal separator
        Locale.setDefault(Locale.US);

        Bank bank = Bank.getInstance();

        Scanner scanner = new Scanner(System.in);

        int numOperations = Integer.parseInt(scanner.nextLine());
        for (int i = 0; i < numOperations; i++) {
            processOperation(scanner.nextLine().split(" "), bank);
        }
    }

    private static void processOperation(String[] operation, Bank bank) {
        switch (operation[0]) {
            case "Create":
                createAccount(operation, bank);
                break;
            case "Deposit":
                deposit(operation, bank);
                break;
            case "Withdraw":
                withdraw(operation, bank);
                break;
            case "Transfer":
                transfer(operation, bank);
                break;
            case "View":
                view(operation, bank);
                break;
            case "Deactivate":
                deactivate(operation, bank);
                break;
            case "Activate":
                activate(operation, bank);
                break;
            default:
                System.out.println("Error: Invalid operation.");
        }
    }

    private static void createAccount(String[] operation, Bank bank) {
        String accountType = operation[2];
        String accountName = operation[3];
        double initialDeposit = Double.parseDouble(operation[4]);

        Account account;
        if (accountType.equalsIgnoreCase("Savings")) {
            account = new SavingsAccount(accountName, initialDeposit);
        } else if (accountType.equalsIgnoreCase("Checking")) {
            account = new CheckingAccount(accountName, initialDeposit);
        } else if (accountType.equalsIgnoreCase("Business")) {
            account = new BusinessAccount(accountName, initialDeposit);
        } else {
            System.out.println("Error: Invalid account type.");
            return;
        }

        bank.createAccount(account);
    }

    private static void deposit(String[] operation, Bank bank) {
        Account depositAccount = bank.getAccount(operation[1]);
        if (depositAccount != null) {
            double depositAmount = Double.parseDouble(operation[2]);
            depositAccount.deposit(depositAmount);
        } else {
            System.out.printf("Error: Account %s does not exist.%n", operation[1]);
        }
    }

    private static void withdraw(String[] operation, Bank bank) {
        Account withdrawAccount = bank.getAccount(operation[1]);
        if (withdrawAccount != null) {
            double withdrawalAmount = Double.parseDouble(operation[2]);
            withdrawAccount.getState().withdraw(withdrawAccount, withdrawalAmount);
        } else {
            System.out.printf("Error: Account %s does not exist.%n", operation[1]);
        }
    }

    private static void transfer(String[] operation, Bank bank) {
        Account fromAccount = bank.getAccount(operation[1]);
        Account toAccount = bank.getAccount(operation[2]);
        if (fromAccount == null) {
            System.out.printf("Error: Account %s does not exist.%n", operation[1]);
        } else if (toAccount == null) {
            System.out.printf("Error: Account %s does not exist.%n", operation[2]);
        } else {
            double transferAmount = Double.parseDouble(operation[3]);
            fromAccount.getState().transfer(fromAccount, toAccount, transferAmount);
        }
    }

    private static void view(String[] operation, Bank bank) {
        Account viewAccount = bank.getAccount(operation[1]);
        if (viewAccount != null) {
            viewAccount.view();
        } else {
            System.out.printf("Error: Account %s does not exist.%n", operation[1]);
        }
    }

    private static void deactivate(String[] operation, Bank bank) {
        Account deactivateAccount = bank.getAccount(operation[1]);
        if (deactivateAccount != null) {
            deactivateAccount.deactivate();
        } else {
            System.out.printf("Error: Account %s does not exist.%n", operation[1]);
        }
    }

    private static void activate(String[] operation, Bank bank) {
        Account activateAccount = bank.getAccount(operation[1]);
        if (activateAccount != null) {
            activateAccount.activate();
        } else {
            System.out.printf("Error: Account %s does not exist.%n", operation[1]);
        }
    }
}

// Singleton
class Bank {
    private static Bank instance;
    private final Map<String, Account> accounts;

    private Bank() {
        accounts = new HashMap<>();
    }

    public static Bank getInstance() {
        if (instance == null) {
            instance = new Bank();
        }
        return instance;
    }

    public void createAccount(Account account) {
        if (!accounts.containsKey(account.getName())) {
            accounts.put(account.getName(), account);
            System.out.printf("A new %s account created for %s with an initial balance of $%.3f.%n",
                    account.getAccountType(), account.getName(), account.getBalance());
        } else {
            System.out.printf("Error: Account %s already exists.%n", account.getName());
        }
    }

    public Account getAccount(String name) {
        return accounts.get(name);
    }
}

// State
interface State {

    void withdraw(Account account, double amount);
    void transfer(Account fromAccount, Account toAccount, double amount);
    String getState();
}

class ActiveState implements State {
    @Override
    public void withdraw(Account account, double amount) {
        account.withdraw(amount);
    }
    @Override
    public void transfer(Account fromAccount, Account toAccount, double amount) { fromAccount.transfer(toAccount, amount);}
    @Override
    public String getState() {
        return "Active";
    }
}

class InactiveState implements State {
    @Override
    public void withdraw(Account account, double amount) {
        System.out.printf("Error: Account %s is inactive.%n", account.getName());
    }
    @Override
    public void transfer(Account fromAccount, Account toAccount, double amount) { System.out.printf("Error: Account %s is inactive.%n", fromAccount.getName());}
    @Override
    public String getState() {
        return "Inactive";
    }
}

// Strategy
interface TransactionStrategy {
    double getTransactionFee(double amount);
}

class SavingsTransactionStrategy implements TransactionStrategy {
    @Override
    public double getTransactionFee(double amount) {
        return amount * 0.015;
    }
}

class CheckingTransactionStrategy implements TransactionStrategy {
    @Override
    public double getTransactionFee(double amount) {
        return amount * 0.02;
    }
}

class BusinessTransactionStrategy implements TransactionStrategy {
    @Override
    public double getTransactionFee(double amount) {
        return amount * 0.025;
    }
}

abstract class Account {
    protected String name;
    protected double balance;
    protected State state;
    protected TransactionStrategy transactionStrategy;
    protected List<String> transactionHistory;

    public Account(String name, double initialBalance, State state, TransactionStrategy transactionStrategy) {
        this.name = name;
        this.balance = initialBalance;
        this.state = state;
        this.transactionStrategy = transactionStrategy;
        this.transactionHistory = new ArrayList<>();
        transactionHistory.add(String.format("Initial Deposit $%.3f", initialBalance));
    }

    public State getState() {
        return state;
    }

    public String getName() {
        return name;
    }

    public double getBalance() {
        return balance;
    }

    public void deposit(double amount) {
        balance += amount;
        transactionHistory.add(String.format("Deposit $%.3f", amount));
        System.out.printf("%s successfully deposited $%.3f. New Balance: $%.3f.%n", name, amount, balance);
    }
    protected void setBalance(double amount) {
        balance+=amount;
    }
    public void withdraw(double amount) {
        double fee = transactionStrategy.getTransactionFee(amount);
        if (balance >= amount) {
            balance -= amount;
            transactionHistory.add(String.format("Withdrawal $%.3f", amount));
            System.out.printf("%s successfully withdrew $%.3f. New Balance: $%.3f. Transaction Fee: $%.3f (%.1f%%) in the system.%n",
                    name, amount - fee, balance, fee, fee / amount * 100);

        } else {
            System.out.printf("Error: Insufficient funds for %s.%n", name);
        }
    }

    public void transfer(Account toAccount, double amount) {
        double fee = transactionStrategy.getTransactionFee(amount);
        if (this.state.getState().equals("Inactive")) {
            System.out.printf("Error: Account %s is inactive.%n", this.getName());
        } else if (balance >= amount) {
            balance -= amount;
            toAccount.setBalance(amount - fee);
            transactionHistory.add(String.format("Transfer $%.3f", amount));
            System.out.printf("%s successfully transferred $%.3f to %s. New Balance: $%.3f. Transaction Fee: $%.3f (%.1f%%) in the system.%n",
                    name, amount - fee, toAccount.getName(), balance, fee, fee / amount * 100);
        } else  {
            System.out.printf("Error: Insufficient funds for %s.%n", name);
        }
    }

    public void view() {
        System.out.printf("%s's Account: Type: %s, Balance: $%.3f, State: %s, Transactions: %s.%n",
                name, getAccountType(), balance, state.getState(), transactionHistory);
    }

    public void activate() {
        if (state instanceof InactiveState) {
            state = new ActiveState();
            System.out.printf("%s's account is now activated.%n", name);
        } else {
            System.out.printf("Error: Account %s is already activated.%n", name);
        }
    }

    public void deactivate() {
        if (state instanceof ActiveState) {
            state = new InactiveState();
            System.out.printf("%s's account is now deactivated.%n", name);
        } else {
            System.out.printf("Error: Account %s is already deactivated.%n", name);
        }
    }

    public abstract String getAccountType();
}

class SavingsAccount extends Account {
    public SavingsAccount(String name, double initialBalance) {
        super(name, initialBalance, new ActiveState(), new SavingsTransactionStrategy());
    }

    @Override
    public String getAccountType() {
        return "Savings";
    }
}

class CheckingAccount extends Account {
    public CheckingAccount(String name, double initialBalance) {
        super(name, initialBalance, new ActiveState(), new CheckingTransactionStrategy());
    }

    @Override
    public String getAccountType() {
        return "Checking";
    }
}

class BusinessAccount extends Account {
    public BusinessAccount(String name, double initialBalance) {
        super(name, initialBalance, new ActiveState(), new BusinessTransactionStrategy());
    }

    @Override
    public String getAccountType() {
        return "Business";
    }
}


