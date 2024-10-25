# $1 - a number of tests
# $2 - a C++ version
# $3 - a path to the source file
cd /work
cp "$3" main.cpp
set -e
CFLAGS=(-O2 --std=c++"$2" -o main)
g++ "${CFLAGS[@]}" main.cpp &> /data/output0.txt
set +e
for i in $(seq 0 $(($1-1)))
do
   {
     ln -fs /data/input"$i".txt ./input.txt
     ln -fs /data/output"$i".txt ./output.txt
     rm -f /data/output"$i".txt
     >&2 echo '<<<ARBUZ'"$i"'ARBUZ>>>'
     ./main < /data/input"$i".txt >> ./output.txt 2>&1
   } || true
done
