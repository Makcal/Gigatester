# $1 - a number of tests
# $2 - a C++ version
# $3 - a path to the source file
# $4 - a name of the main file
cd /work
cp "$3" "$4".cpp
set -e
g++ -O2 --std=c++$2 -o $4 ./"$4".cpp &> /data/output0.txt
set +e
for i in `seq 0 $(($1-1))`
do
   {
     ln -fs /data/input"$i".txt ./input.txt
     ln -fs /data/output"$i".txt ./output.txt
     rm -f /data/output"$i".txt
     ./"$4" < /data/input"$i".txt >> ./output.txt 2>&1
   } || true
done
