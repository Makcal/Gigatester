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
public final class UniversityCourseManagementSystem {
    /**
     * A map to store courses by id.
     */
    private static Map<Integer, Course> courses = new HashMap<>();
    /**
     * A map to store students by id.
     */
    private static Map<Integer, Student> students = new HashMap<>();
    /**
     * A map to store professors by id.
     */
    private static Map<Integer, Professor> professors = new HashMap<>();
    /**
     * A scanner to scan input.
     */
    private static Scanner scanner = new Scanner(System.in);
    /**
     * A list of words that can not be a name for courses and members.
     */
    private static Set<String> banList = new HashSet<>();

    /**
     * Main method used to start the program.
     * @param args console arguments
     */
    public static void main(String[] args) {
        fillInitialData();
        banList.add("course");
        banList.add("student");
        banList.add("professor");
        banList.add("enroll");
        banList.add("drop");
        banList.add("teach");
        banList.add("exempt");

        for (String line = getLine();; line = getLine()) {
            switch (line) {
                case "course":
                    addCourse();
                    break;
                case "student":
                    addStudent();
                    break;
                case "professor":
                    addProfessor();
                    break;
                case "enroll":
                    enrollStudent();
                    break;
                case "drop":
                    dropStudent();
                    break;
                case "teach":
                    assignCourse();
                    break;
                case "exempt":
                    exemptProfessor();
                    break;
                default:
                    new WrongInputsException("Unknown command").finishProgram();
                    return;
            }
        }
    }

    /**
     * Performs all required actions to read and add a course.
     */
    private static void addCourse() {
        String name = "";
        try {
            name = readCourseName();
        } catch (WrongInputsException e) {
            e.finishProgram();
        }
        try {
            checkCourseExistence(name);
        } catch (CourseExistsException e) {
            e.finishProgram();
        }

        CourseLevel level = null;
        try {
            level = readCourseLevel();
        } catch (WrongInputsException e) {
            e.finishProgram();
        }

        Course course = new Course(name, level);
        courses.put(course.getCourseId(), course);
        System.out.println("Added successfully");
    }

    /**
     * Checks if a course with the given {@code name} is already in the database.
     * @param name a name of a course
     * @throws CourseExistsException if such a course exists
     */
    private static void checkCourseExistence(String name) throws CourseExistsException {
        for (Course course : courses.values()) {
            if (Objects.equals(course.getCourseName(), name)) {
                throw new CourseExistsException();
            }
        }
    }

    /**
     * Performs all required actions to read and add a student.
     */
    private static void addStudent() {
        String name = "";
        try {
            name = readName();
        } catch (WrongInputsException e) {
            e.finishProgram();
        }

        Student student = new Student(name);
        students.put(student.getMemberId(), student);
        System.out.println("Added successfully");
    }

    /**
     * Performs all required actions to read and add a professor.
     */
    private static void addProfessor() {
        String name = "";
        try {
            name = readName();
        } catch (WrongInputsException e) {
            e.finishProgram();
        }

        Professor professor = new Professor(name);
        professors.put(professor.getMemberId(), professor);
        System.out.println("Added successfully");
    }

    /**
     * Performs all required actions to enroll a student in a course.
     */
    private static void enrollStudent() {
        MemberCoursePair pair = getMemberAndCourse(true);
        Student student = (Student) pair.member;
        Course course = pair.course;
        try {
            student.enroll(course);
        } catch (MyException e) {
            e.finishProgram();
        }
        System.out.println("Enrolled successfully");
    }

    /**
     * Performs all required actions to make a student drop a course.
     */
    private static void dropStudent() {
        MemberCoursePair pair = getMemberAndCourse(true);
        Student student = (Student) pair.member;
        Course course = pair.course;
        try {
            student.drop(course);
        } catch (MyException e) {
            e.finishProgram();
        }
        System.out.println("Dropped successfully");
    }

    /**
     * A util class for storing both {@code UniversityMember} and {@code Course}.
     */
    private static class MemberCoursePair {
        /**
         * A {@code UniversityMember} of the pair.
         */
        private final UniversityMember member;
        /**
         * A {@code Course} of the pair.
         */
        private final Course course;

        /**
         * The simplest constructor.
         * @param member A {@code UniversityMember} of the pair
         * @param course A {@code Course} of the pair
         */
        MemberCoursePair(UniversityMember member, Course course) {
            this.member = member;
            this.course = course;
        }
    }

    /**
     * Performs all required actions to read a member, then a course.
     * @param isStudent to check whether the member is a student or a professor
     * @return A {@code MemberCoursePair} with read data
     */
    private static MemberCoursePair getMemberAndCourse(boolean isStudent) {
        Map<Integer, ? extends UniversityMember> listToFind = isStudent ? students : professors;

        int memberId = 0;
        try {
            memberId = readId();
        } catch (WrongInputsException e) {
            e.finishProgram();
        }
        if (!listToFind.containsKey(memberId)) {
            new WrongInputsException((isStudent ? "Student" : "Professor") + " not found").finishProgram();
        }

        int courseId = 0;
        try {
            courseId = readId();
        } catch (WrongInputsException e) {
            e.finishProgram();
        }
        if (!courses.containsKey(courseId)) {
            new WrongInputsException("Course not found").finishProgram();
        }

        UniversityMember member = listToFind.get(memberId);
        Course course = courses.get(courseId);
        return new MemberCoursePair(member, course);
    }

    /**
     * Performs all required actions to assign a course to a professor.
     */
    private static void assignCourse() {
        MemberCoursePair pair = getMemberAndCourse(false);
        Professor professor = (Professor) pair.member;
        Course course = pair.course;
        try {
            professor.teach(course);
        } catch (MyException e) {
            e.finishProgram();
        }
        System.out.println("Professor is successfully assigned to teach this course");
    }

    /**
     * Performs all required actions to exempt a professor from a course.
     */
    private static void exemptProfessor() {
        MemberCoursePair pair = getMemberAndCourse(false);
        Professor professor = (Professor) pair.member;
        Course course = pair.course;
        try {
            professor.exempt(course);
        } catch (MyException e) {
            e.finishProgram();
        }
        System.out.println("Professor is exempted");
    }

    /**
     * Reads a new line from input and stops the program if it is empty.
     * @return The read line
     */
    private static String getLine() {
        try {
            String line = scanner.nextLine();
            if (Objects.equals(line, "")) {
                System.exit(0);
            }
            return line;
        } catch (Exception e) {
            System.exit(0);
            return "";
        }
    }

    /**
     * Reads a {@code UniversityMember} name and validates it.
     * @return The read name
     * @throws WrongInputsException if the name does not match the allowed pattern
     */
    private static String readName() throws WrongInputsException {
        String name = getLine().toLowerCase();
        if (!name.matches("[a-z]+") || banList.contains(name)) {
            throw new WrongInputsException("Invalid name");
        }
        return name;
    }

    /**
     * Reads a {@code Course} name and validates it.
     * @return The read course name
     * @throws WrongInputsException if the course name does not match the allowed pattern
     */
    private static String readCourseName() throws WrongInputsException {
        String name = getLine().toLowerCase();
        if (!name.matches("[a-z]+(_[a-z]+)*") || banList.contains(name)) {
            throw new WrongInputsException("Invalid course name");
        }
        return name;
    }

    /**
     * Reads a {@code Course} level and validates it.
     * @return The read course level
     * @throws WrongInputsException if the value is not allowed
     */
    private static CourseLevel readCourseLevel() throws WrongInputsException {
        String level = getLine().toLowerCase();
        switch (level) {
            case "bachelor":
                return CourseLevel.BACHELOR;
            case "master":
                return CourseLevel.MASTER;
            default:
                throw new WrongInputsException("Invalid course level");
        }
    }

    /**
     * Reads an id and validates it.
     * @return The read id
     * @throws WrongInputsException if the id is not a number
     */
    private static int readId() throws WrongInputsException {
        try {
            String line = getLine();
            int id = Integer.parseInt(line);
            if (id < 1) {
                throw new WrongInputsException("Invalid id");
            }
            return id;
        } catch (NumberFormatException e) {
            throw new WrongInputsException("Integer parsing error");
        }
    }

    /**
     * Fills the storage with initial instances.
     */
    public static void fillInitialData() {
        Course javaBeginner = new Course("java_beginner", CourseLevel.BACHELOR);
        courses.put(javaBeginner.getCourseId(), javaBeginner);
        Course javaIntermediate = new Course("java_intermediate", CourseLevel.BACHELOR);
        courses.put(javaIntermediate.getCourseId(), javaIntermediate);
        Course pythonBasics = new Course("python_basics", CourseLevel.BACHELOR);
        courses.put(pythonBasics.getCourseId(), pythonBasics);
        Course algorithms = new Course("algorithms", CourseLevel.MASTER);
        courses.put(algorithms.getCourseId(), algorithms);
        Course advancedProgramming = new Course("advanced_programming", CourseLevel.MASTER);
        courses.put(advancedProgramming.getCourseId(), advancedProgramming);
        Course mathematicalAnalysis = new Course("mathematical_analysis", CourseLevel.MASTER);
        courses.put(mathematicalAnalysis.getCourseId(), mathematicalAnalysis);
        Course course = new Course("computer_vision", CourseLevel.MASTER);
        courses.put(course.getCourseId(), course);

        try {
            Student student = new Student("Alice");
            student.enroll(javaBeginner);
            student.enroll(javaIntermediate);
            student.enroll(pythonBasics);
            students.put(student.getMemberId(), student);
            student = new Student("Bob");
            student.enroll(javaBeginner);
            student.enroll(algorithms);
            students.put(student.getMemberId(), student);
            student = new Student("Alex");
            student.enroll(advancedProgramming);
            students.put(student.getMemberId(), student);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }

        try {
            Professor professor = new Professor("Ali");
            professor.teach(javaBeginner);
            professor.teach(javaIntermediate);
            professors.put(professor.getMemberId(), professor);
            professor = new Professor("Ahmed");
            professor.teach(pythonBasics);
            professor.teach(advancedProgramming);
            professors.put(professor.getMemberId(), professor);
            professor = new Professor("Andrey");  // why not Nikolay Shilov?
            professor.teach(mathematicalAnalysis);
            professors.put(professor.getMemberId(), professor);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Stupid redundant constructor.
     */
    private UniversityCourseManagementSystem() { }
}

/**
 * Base for {@code Student} and {@code Professor}
 */
abstract class UniversityMember {
    /**
     * Current number of students and professors.
     */
    private static int numberOfMembers = 0;
    /**
     * A unique ID of the member.
     */
    private int memberId;
    /**
     * Member's name.
     */
    private String memberName;

    /**
     * Getter for {@code numberOfMembers}
     * @return value of {@code numberOfMembers}
     */
    public static int getNumberOfMembers() {
        return numberOfMembers;
    }

    /**
     * Setter for {@code numberOfMembers}
     * @param numberOfMembers value to set
     */
    public static void setNumberOfMembers(int numberOfMembers) {
        UniversityMember.numberOfMembers = numberOfMembers;
    }

    /**
     * Returns the next free ID for members.
     * @return the next ID
     */
    public static int getNewId() {
        setNumberOfMembers(getNumberOfMembers() + 1);
        return getNumberOfMembers();
    }

    /**
     * Getter for {@code memberId}
     * @return value of {@code memberId}
     */
    protected int getMemberId() {
        return memberId;
    }

    /**
     * Setter for {@code memberId}
     * @param memberId value to set
     */
    private void setMemberId(int memberId) {
        this.memberId = memberId;
    }

    /**
     * Setter for {@code memberName}
     * @param memberName value to set
     */
    protected void setMemberName(String memberName) {
        this.memberName = memberName;
    }

    /**
     * Constructor that takes member's ID and name.
     * @param memberId member's ID
     * @param memberName member's name
     */
    public UniversityMember(int memberId, String memberName) {
        setMemberId(memberId);
        setMemberName(memberName);
    }
}

/**
 * Course contains general information about a course in the university.
 */
class Course {
    /**
     * Maximum number of students who can take the course.
     */
    private static final int CAPACITY = 3;
    /**
     * Current number of courses.
     */
    private static int numberOfCourses = 0;
    /**
     * A unique ID of the course.
     */
    private int courseId;
    /**
     * Course's name
     */
    private String courseName;
    /**
     * A list of students who has taken the course.
     */
    private final List<Student> enrolledStudents = new ArrayList<>();
    /**
     * A list of professors who teach the course.
     */
    private List<Professor> teachers = new ArrayList<>();
    /**
     * The level of the course.
     */
    private CourseLevel courseLevel;

    /**
     * Getter for {@code numberOfCourses}
     * @return value of {@code numberOfCourses}
     */
    private static int getNumberOfCourses() {
        return numberOfCourses;
    }

    /**
     * Setter for {@code numberOfCourses}
     * @param numberOfCourses value to set
     */
    private static void setNumberOfCourses(int numberOfCourses) {
        Course.numberOfCourses = numberOfCourses;
    }

    /**
     * Returns the next free ID for courses.
     * @return the next ID
     */
    public static int getNewId() {
        setNumberOfCourses(getNumberOfCourses() + 1);
        return getNumberOfCourses();
    }

    /**
     * Getter for {@code courseId}
     * @return value of {@code courseId}
     */
    public int getCourseId() {
        return courseId;
    }

    /**
     * Getter for {@code courseName}
     * @return value of {@code courseName}
     */
    public String getCourseName() {
        return courseName;
    }

    /**
     * Getter for {@code enrolledStudents}
     * @return value of {@code enrolledStudents}
     */
    public List<Student> getEnrolledStudents() {
        return enrolledStudents;
    }

    /**
     * Getter for {@code teachers}
     * @return value of {@code teachers}
     */
    public List<Professor> getTeachers() {
        return teachers;
    }

    /**
     * Constructor that takes course's name and level.
     * @param courseName member's ID
     * @param courseLevel member's name
     */
    public Course(String courseName, CourseLevel courseLevel) {
        courseId = getNewId();
        this.courseName = courseName;
        this.courseLevel = courseLevel;
    }

    /**
     * Checks if the maximum of students is reached
     * @return if the maximum of students is reached
     */
    public boolean isFull() {
         return getEnrolledStudents().size() == CAPACITY;
    }
}

/**
 * Professor can give courses and can be exempted from them.
 */
class Professor extends UniversityMember {
    /**
     * Maximum number of courses that a professor can give.
     */
    private static final int MAX_LOAD = 2;
    /**
     * A list of courses that the professor give.
     */
    private final List<Course> assignedCourses = new ArrayList<>();

    /**
     * Simple constructor that takes professor's name.
     * @param memberName professor's name
     */
    public Professor(String memberName) {
        super(UniversityMember.getNewId(), memberName);
    }

    /**
     * Assigns the professor to a course.
     * @param course course which the professor should give
     * @return whether the assignation was successful
     * @throws MaximumLoadException if professor's load is complete
     * @throws AlreadyTeachingException if the professor is already teaching the course
     */
    public boolean teach(Course course) throws MaximumLoadException, AlreadyTeachingException {
        if (assignedCourses.size() >= MAX_LOAD) {
            throw new MaximumLoadException();
        }
        if (course.getTeachers().contains(this)) {
            throw new AlreadyTeachingException();
        }

        assignedCourses.add(course);
        course.getTeachers().add(this);
        return true;
    }

    /**
     * Exempts the professor from giving a course.
     * @param course a course from which the professor should be exempted
     * @return whether the exemption was successful
     * @throws NotTeachingException if the professor does not give the course
     */
    public boolean exempt(Course course) throws NotTeachingException {
        if (!course.getTeachers().contains(this)) {
            throw new NotTeachingException();
        }

        course.getTeachers().remove(this);
        return assignedCourses.remove(course);
    }
}

/**
 * A student can enroll or drop courses.
 */
class Student extends UniversityMember implements Enrollable {
    /**
     * Maximum number of courses that a student can have.
     */
    private static final int MAX_ENROLLMENT = 3;
    /**
     * A list of courses that the student has.
     */
    private final List<Course> enrolledCourses = new ArrayList<>();

    /**
     * Simple constructor that takes student's name.
     * @param memberName student's name
     */
    public Student(String memberName) {
        super(UniversityMember.getNewId(), memberName);
    }

    /**
     * Drops the student from a course.
     * @param course a course from which the student should be dropped
     * @return whether the drop was successful
     * @throws NotEnrolledException if the student is not enrolled in the course
     */
    public boolean drop(Course course) throws NotEnrolledException {
        if (!enrolledCourses.contains(course) || !course.getEnrolledStudents().contains(this)) {
            throw new NotEnrolledException();
        }
        return enrolledCourses.remove(course) && course.getEnrolledStudents().remove(this);
    }

    /**
     * Enrolls the student in a course.
     * @param course a course in which the student should be enrolled in
     * @return whether the enrollment was successful
     * @throws AlreadyEnrolledException if the student is already enrolled
     * @throws MaximumEnrollmentException if the student can not have any more courses
     * @throws CourseFullException if the given course can not fit more students
     */
    public boolean enroll(Course course) throws AlreadyEnrolledException, MaximumEnrollmentException,
            CourseFullException {
        if (course.getEnrolledStudents().contains(this) || enrolledCourses.contains(course)) {
            throw new AlreadyEnrolledException();
        }
        if (enrolledCourses.size() >= MAX_ENROLLMENT) {
            throw new MaximumEnrollmentException();
        }
        if (course.isFull()) {
            throw new CourseFullException();
        }

        enrolledCourses.add(course);
        course.getEnrolledStudents().add(this);
        return true;
    }
}

/**
 * Some interface that is never used
 */
interface Enrollable {
    /**
     * Drops the student from a course.
     * @param course a course from which the student should be dropped
     * @return whether the drop was successful
     * @throws NotEnrolledException if the student is not enrolled in the course
     */
    boolean drop(Course course) throws NotEnrolledException;
    /**
     * Enrolls the student in a course.
     * @param course a course in which the student should be enrolled in
     * @return whether the enrollment was successful
     * @throws AlreadyEnrolledException if the student is already enrolled
     * @throws MaximumEnrollmentException if the student can not have any more courses
     * @throws CourseFullException if the given course can not fit more students
     */
    boolean enroll(Course course) throws AlreadyEnrolledException, MaximumEnrollmentException, CourseFullException;
}

enum CourseLevel {
    BACHELOR, MASTER
}

/**
 * A base class for all possible errors in the program.
 */
class MyException extends Exception {
    /**
     * A message to be displayed when the program finishes
     */
    private final String errorMessage;

    /**
     * Simple constructor
     * @param finalMessage an error message
     */
    MyException(String finalMessage) {
        super();
        this.errorMessage = finalMessage;
    }

    /**
     * Takes an extra error description
     * @param message an extra error description
     * @param finalMessage an error message
     */
    MyException(String message, String finalMessage) {
        super(message);
        this.errorMessage = finalMessage;
    }

    /**
     * Finishes the program and displays the error message
     */
    public void finishProgram() {
        System.out.println(errorMessage);
        System.exit(0);
    }
}

class CourseExistsException extends MyException {
    CourseExistsException() {
        super("Course exists");
    }
}

class AlreadyEnrolledException extends MyException {
    AlreadyEnrolledException() {
        super("Student is already enrolled in this course");
    }
}

class MaximumEnrollmentException extends MyException {
    MaximumEnrollmentException() {
        super("Maximum enrollment is reached for the student");
    }
}

class CourseFullException extends MyException {
    CourseFullException() {
        super("Course is full");
    }
}

class NotEnrolledException extends MyException {
    NotEnrolledException() {
        super("Student is not enrolled in this course");
    }
}

class MaximumLoadException extends MyException {
    MaximumLoadException() {
        super("Professor's load is complete");
    }
}

class AlreadyTeachingException extends MyException {
    AlreadyTeachingException() {
        super("Professor is already teaching this course");
    }
}

class NotTeachingException extends MyException {
    NotTeachingException() {
        super("Professor is not teaching this course");
    }
}

class WrongInputsException extends MyException {
    WrongInputsException(String message) {
        super(message, "Wrong inputs");
    }
}
