--- 
+++ 
@@ -40,7 +40,10 @@
     } else {
       // In this case, the name was implicitly provided by two independent
       // modules. We need to move this code up to a common module.
-      int indexOfDot = namespace.indexOf('.');
+      int indexOfDot = namespace.lastIndexOf('.');
+      if (indexOfDot == -1) {
+        indexOfDot = namespace.lastIndexOf('/');
+      }
       if (indexOfDot == -1) {
         // Any old place is fine.
         compiler.getNodeForCodeInsertion(minimumModule)