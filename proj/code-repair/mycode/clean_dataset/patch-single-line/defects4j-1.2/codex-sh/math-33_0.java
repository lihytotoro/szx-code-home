--- 
+++ 
@@ -9,7 +9,7 @@
     // positive cost non-artificial variables
     for (int i = getNumObjectiveFunctions(); i < getArtificialVariableOffset(); i++) {
         final double entry = tableau.getEntry(0, i);
-        if (Precision.compareTo(entry, 0d, maxUlps) > 0) {
+        if (Precision.compareTo(entry, 0d, epsilon) > 0) {
             columnsToDrop.add(i);
         }
     }
