--- 
+++ 
@@ -46,7 +46,7 @@
 
     // Check if the sources need to be re-ordered.
     boolean staleInputs = false;
-    if (options.dependencyOptions.needsManagement() && options.closurePass) {
+    if (getOptions().dependencyOptions.needsManagement()) {
       for (CompilerInput input : inputs) {
         // Forward-declare all the provided types, so that they
         // are not flagged even if they are dropped from the process.
