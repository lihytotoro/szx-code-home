--- 
+++ 
@@ -24,7 +24,7 @@
     txt = txt.replaceAll("^gn", "2n");
 
     // End 
-    txt = txt.replaceAll("^mb", "m2");
+    txt = txt.replaceAll("mb$", "m2");
 
     // 4. Handle replacements
     txt = txt.replaceAll("cq", "2q");
