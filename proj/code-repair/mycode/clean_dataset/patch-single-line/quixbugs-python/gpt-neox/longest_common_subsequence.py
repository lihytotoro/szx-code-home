--- 
+++ 
@@ -3,7 +3,7 @@
         return ''
 
     elif a[0] == b[0]:
-        return a[0] + longest_common_subsequence(a[1:], b)
+        return a[0] + longest_common_subsequence(a[1:], b[1:])
 
     else:
         return max(
