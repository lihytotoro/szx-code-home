--- 
+++ 
@@ -2,4 +2,7 @@
     if b == 0:
         return a
     else:
-        return gcd(a % b, b)
+        return gcd(b, a % b)
+
+
+
