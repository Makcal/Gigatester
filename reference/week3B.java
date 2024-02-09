import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Scanner;
import java.util.Set;

/**
 * Class UniversityCourseManagementSystem for managing courses, students and professors.
 */
public final class Main {
    public static void main(String[] args) {
        Scanner s = new Scanner(System.in);
        int n = s.nextInt();
        s.nextLine();
        String[] ss = s.nextLine().split(" ");
        Set<String> a = new HashSet<>(), b = new HashSet<>(), c = new HashSet<>();
        for (String r : ss) {
            a.add(r);
        }

        int m = s.nextInt();
        s.nextLine();
        ss = s.nextLine().split(" ");
        for (String r : ss) {
            b.add(r);
        }

        List<String> l = new ArrayList<>();
        for (String r : ss) {
            if (c.contains(r) || a.contains(r)) continue;
            c.add(r);
            l.add(r);
        }
        System.out.println(l.size());
        for (String r : l) {
            System.out.println(r);
        }
    }
}
