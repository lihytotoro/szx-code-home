--- 
+++ 
@@ -17,7 +17,7 @@
             }
 
             double sumWts = 0;
-            for (int i = 0; i < weights.length; i++) {
+            for (int i = begin; i < begin + length; i++) {
                 sumWts += weights[i];
             }
 
