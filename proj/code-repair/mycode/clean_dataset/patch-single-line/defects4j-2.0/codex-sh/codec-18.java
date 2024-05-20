--- 
+++ 
@@ -8,5 +8,5 @@
     if (cs1 instanceof String && cs2 instanceof String) {
         return cs1.equals(cs2);
     }
-    return CharSequenceUtils.regionMatches(cs1, false, 0, cs2, 0, Math.max(cs1.length(), cs2.length()));
+    return cs1.length() == cs2.length() && CharSequenceUtils.regionMatches(cs1, false, 0, cs2, 0, cs1.length());
 }
