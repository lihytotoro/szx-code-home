--- 
+++ 
@@ -6,7 +6,7 @@
         if x < arr[mid]:
             return binsearch(start, mid)
         elif x > arr[mid]:
-            return binsearch(mid, end)
+            return binsearch(mid+1, end)
         else:
             return mid
 
