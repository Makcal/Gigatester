# $1 - a number of tests
# $2 - a path to the source file
# $3 - a name of the main class
cd /work
cp "$2" /work/"$3".java
set -e
javac /work/"$3".java &> /data/output0.txt
set +e
for i in `seq 0 $(($1-1))`
do
   {
     java -XX:+UseSerialGC -XX:TieredStopAtLevel=1 -XX:NewRatio=5 -Xms8M -Xmx256M -Xss64M -DONLINE_JUDGE=true "$3" < /data/input"$i".txt &> /data/output"$i".txt
   } || true
done
