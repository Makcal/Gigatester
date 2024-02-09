import java.util.*;

/**
 * Class UniversityCourseManagementSystem for managing courses, students and professors.
 */
public final class Main {
    public static void main(String[] args) {
        Scanner s = new Scanner(System.in);
        int n = s.nextInt();
        TreeMap<String, Integer> map = new TreeMap<>();
        s.nextLine();
        for (int i = 0; i < n; i++) {
            String ss = s.next();
            if (map.containsKey(ss)) {
                map.put(ss, map.get(ss)+1);
            }
            else {
                map.put(ss, 1);
            }
        }

        ArrayList<A> ar = new ArrayList<>();
        for (Map.Entry<String, Integer> e : map.entrySet()) {
            A a = new A();
            a.s = e.getKey();
            a.n = e.getValue();
            ar.add(a);
        }
        ar.sort(new Comparator<A>() {
            public int compare(A a, A b) {
                if (a.n == b.n) {
                    return a.s.compareTo(b.s);
                }
                return -(a.n - b.n);
            }
        });

        for (A a : ar) {
            System.out.println(a.s + " " + a.n);
        }
    }
}

class A {
    String s;
    int n;
}
