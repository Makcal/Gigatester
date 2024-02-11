# $1 - a number of tests
# $2 - a path to the source file
# $3 - a name of the main class
cd /work
cp "$2" /work/"$3".java
set -e
javac /work/"$3".java &> /data/output0.txt
for i in `seq 0 $(($1-1))`
do
   {
     cat /data/input"$i".txt | java "$3" &> /data/output"$i".txt
   } || echo
done
