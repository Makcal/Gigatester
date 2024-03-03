# $1 - a number of tests
# $2 - a path to the source file
# $3 - a name of the main class
cd /work
cp "$2" "$3".cpp
set -e
g++ -O2 --std=c++17 -o $3 ./"$3".cpp &> /data/output0.txt
set +e
for i in `seq 0 $(($1-1))`
do
   {
     ./"$3" < /data/input"$i".txt &> /data/output"$i".txt
   } || true
done
