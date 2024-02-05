import sys
import os
import random
import subprocess
import time
import concurrent.futures
import shutil

"""
ACKNOWLEDGEMENTS:
1) Anonymous author who released the previous version for the 3rd assignment before me. Some their ideas were applied here.
2) Ravil Kazeev who helped me with some testing on Windows
3) All people who need help
"""

global java_path

MAX_DEPTH = 5
p = 0.6


def generate():
    if random.random() < 0.2:
        n, m = random.randint(1, 10**5), random.randint(1, 10**5)
        bb = 1
    else:
        n, m = random.randint(1, 20), random.randint(1, 20)
        bb = 0
    s = set()
    alph = "abcdefgxyz"
    for i in range((n+m)*10 if not bb else (n+m)*2):
        w = ""
        for _ in range(random.randint(1, 8)):
            w += random.choice(alph)
        while w in s and not bb:
            w = ""
            for _ in range(random.randint(1, 8)):
                w += random.choice(alph)
        s.add(w)
    s = list(s)
    r = f"{n}\n"
    r += " ".join(random.choices(s, k=n)) + "\n"
    r += f"{m}\n"
    r += " ".join(random.choices(s, k=m)) + "\n"
    return r


def run_test(n, test):
    fout = open(f'output{n}.txt', 'w')
    o = subprocess.run([java_path+'java', '-jar', f'Jar{n}.jar'], capture_output=True, input=test.encode()).stdout.decode()
    fout.write(o)
    fout.close()
    return o


def main():
    global java_path
    n, p1, p2 = sys.argv[1:4]
    if len(sys.argv) >= 5:
        java_path = sys.argv[4] + os.sep
    else:
        java_path = ""

    try:
        os.mkdir('build1')
    except Exception:
        shutil.rmtree('build1')
        os.mkdir('build1')
    subprocess.run([java_path+'javac', '-d', 'build1/', p1])
    subprocess.run([java_path+'jar', 'cfe', 'Jar1.jar', 'UniversityCourseManagementSystem', '-C', 'build1', '.'])

    try:
        os.mkdir('build2')
    except Exception:
        shutil.rmtree('build2')
        os.mkdir('build2')
    subprocess.run([java_path+'javac', '-d', 'build2/', p2])
    subprocess.run([java_path+'jar', 'cfe', 'Jar2.jar', 'UniversityCourseManagementSystem', '-C', 'build2', '.'])

    ts = time.time()

    for _ in range(int(n)):
        test = generate()

        fin = open('input.txt', 'w')
        fin.write(test)
        fin.close()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            o1, o2 = executor.map(run_test, (1, 2), (test, test))

        if o1 != o2:
            print("Difference!")
            exit(0)

    print("OK")
    print("Time: " + str(time.time() - ts))


if __name__ == '__main__':
    main()