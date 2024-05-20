--- 
+++ 
@@ -3,7 +3,7 @@
         return len(source) or len(target)
 
     elif source[0] == target[0]:
-        return 1 + levenshtein(source[1:], target[1:])
+        return levenshtein(source[1:], target[1:])
 
     else:
         return 1 + min(
