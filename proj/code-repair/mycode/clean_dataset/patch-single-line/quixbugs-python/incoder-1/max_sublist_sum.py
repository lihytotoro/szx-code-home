--- 
+++ 
@@ -3,7 +3,7 @@
     max_so_far = 0
 
     for x in arr:
-        max_ending_here = max_ending_here + x
+        max_ending_here = max(max_ending_here+x, 0)
         max_so_far = max(max_so_far, max_ending_here)
 
     return max_so_far
