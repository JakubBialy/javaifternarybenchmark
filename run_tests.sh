#!/usr/bin/env bash

set -e
set -o pipefail

JDKS=(
$LT_JAVA_8
$LT_JAVA_11
$LT_JAVA_12
$LT_JAVA_13
$LT_JAVA_14
$LT_JAVA_15
$LT_JAVA_16
)

timestamp=$(date +"%Y%m%d%_k%M%N")
outputDir=./data/$timestamp
mkdir -p $outputDir

for item in ${JDKS[*]}
do
        curr_java_ver=$(JAVA_HOME=$item python3 ./get_java_version.py)
        curr_java_major_ver=$(JAVA_HOME=$item python3 ./get_java_major_version.py)

        printf "Java version: $curr_java_ver\n"
        printf "Java major version: $curr_java_major_ver\n\n"
        JAVA_HOME=$(echo $item) mvn -Djdk.ver=$curr_java_major_ver clean package

        $item/bin/java -jar ./target/Java_Benchmarks-0.1.0.jar FindMaxBenchmark -jvmArgs -XX:+UseG1GC -bm thrpt -wi 10 -w 10 -r 10 -i 50 -f 2 -rf scsv -rff $outputDir/benchmark_$curr_java_ver.scsv -prof 'perfasm:intelSyntax=true' | tee $outputDir/benchmark_$curr_java_ver.log
done

python3 ./generate_plot2.py --input-dir $outputDir --output-file plot_$timestamp.png --first-dimen java_version --second-dimen Benchmark --third-dimen Score --output-mode multi_plot --extract-jdk-version --remove-second-dimen-common-prefixes --error-name "Score Error (99.9%)"
