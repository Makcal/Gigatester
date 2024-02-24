import java.util.*;

/**
 * Class UniversityCourseManagementSystem for managing courses, students and professors.
 */
public final class Main {
    public static void main(String[] args) {
        Scanner s = new Scanner(System.in);
        int n = s.nextInt();
        ArrayList<A> ar = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            int r = s.nextInt();
            String ss = s.next() + " " + s.next();
            A a = new A();
            a.n = r;
            a.s = ss;
            ar.add(a);
        }

        ar.sort(new Comparator<A>() {
            public int compare(A a, A b) {
                return (a.n - b.n);
            }
        });

        System.out.println(ar.get(n/2).s);
    }
}

class A {
    String s;
    int n;
}
