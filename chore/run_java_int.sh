# $1 - a number of tests
# $2 - a path to the source file
# $3 - a name of the main class
cd /work
cp "$2" /work/"$3".java
{
    javac /work/"$3".java
} || {
    echo CompilationError > /data/to_py
    exit 1
}
JAVA_FLAGS=(-XX:+UseSerialGC '-XX:TieredStopAtLevel=1' '-XX:NewRatio=5' -Xms8M -Xmx256M -Xss64M '-DONLINE_JUDGE=true')

echo Start > /data/to_py
for i in $(seq 0 $(($1-1)))
do
   {
     cat /data/to_cont > /dev/null
     java "${JAVA_FLAGS[@]}" "$3" </data/prog_in >/data/prog_out 2>&1 &
     disown 2> /dev/null
     cat /data/to_cont > /dev/null
     kill $! 2> /dev/null || true
   } || true
done
