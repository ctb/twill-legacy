Code generator for MaxQ
=======================

MaxQ is a tool that records you using a web site. It turns the links you click
on and any other input into a Python script that you can play back at any time.

This directory contains a twill script generator for MaxQ. To use it,

 1. get the MaxQ source from http://maxq.tigris.org,

 2. copy the TwillScriptGenerator.java file into the
    java/com/bitmechanic/maxq/generator directory under the MaxQ source;

 3. run 'ant' to recompile maxq,

 4. add "com.bitmechanic.maxq.generator.TwillScriptGenerator" into the
    conf/maxq.properties file,

 5. run bin/maxq.

Please let me know if you run into any problems.

--titus

titus@caltech.edu
