# $1 - a number of tests
# $2 - a C++ version
# $3 - a path to the source file
cd /work
cp "$3" main.cpp
{
    CFLAGS=(-O2 --std=c++"$2" -o main)
    g++ "${CFLAGS[@]}" main.cpp
} || {
    echo CompilationError > /data/to_py
    exit 1
}

echo Start > /data/to_py
for i in $(seq 0 $(($1-1)))
do
   {
     cat /data/to_cont > /dev/null
     echo '<<<ARBUZ'"$i"'ARBUZ>>>'
     ./main </data/prog_in >/data/prog_out &
     cat /data/to_cont > /dev/null
     kill $! 2> /dev/null || true
   } || true
done
