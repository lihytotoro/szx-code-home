--- 
+++ 
@@ -1,3 +1,3 @@
 public double getPct(Object v) {
-    return getCumPct((Comparable<?>) v);
+    return getPct(((Integer) v).intValue());
 }
