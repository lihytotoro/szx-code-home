--- 
+++ 
@@ -47,7 +47,6 @@
 
     // Check if the sources need to be re-ordered.
     if (options.dependencyOptions.needsManagement() &&
-        !options.skipAllPasses &&
         options.closurePass) {
       for (CompilerInput input : inputs) {
         // Forward-declare all the provided types, so that they
