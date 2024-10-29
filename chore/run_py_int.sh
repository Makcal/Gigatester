# $1 - a number of tests
# $2 - a path to the source file
cd /work || exit 1
cp "$2" main.py

echo Start > /data/to_py
for i in $(seq 0 $(($1-1)))
do
   {
     cat /data/to_cont > /dev/null
     python3 main.py </data/prog_in >/data/prog_out 2>&1 &
     disown 2> /dev/null
     cat /data/to_cont > /dev/null
     kill $! 2> /dev/null || true
   } || true
done
