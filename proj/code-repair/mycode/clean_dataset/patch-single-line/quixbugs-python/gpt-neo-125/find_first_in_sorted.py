--- 
+++ 
@@ -2,7 +2,7 @@
     lo = 0
     hi = len(arr)
 
-    while lo <= hi:
+    while lo < hi:
         mid = (lo + hi) // 2
 
         if x == arr[mid] and (mid == 0 or x != arr[mid - 1]):
