#!/bin/bash
# Compila el núcleo AS3 (src/core) -> work/core/JMCore.swf y extrae su ABC -> work/core/JMCore-0.abc
D=/c/Mods/jacksmith
J="$D/tools/jre/jdk-21.0.12.1+1-jre/bin/java.exe"
mkdir -p $D/work/core && rm -f $D/work/core/*
"$J" -Dsun.io.useCanonCaches=false -Xmx1g -jar "$D/tools/flex/lib/mxmlc.jar" "+flexlib=$D/tools/flex/frameworks" "-load-config=$D/src/core/jm-config.xml" -output "$D/work/core/JMCore.swf" "$D/src/core/JMCore.as" 2>&1 | grep -v "^$" | tail -30
[ -f $D/work/core/JMCore.swf ] || exit 1
"$D/tools/rabcdasm/abcexport.exe" "$D/work/core/JMCore.swf" && ls -la $D/work/core
