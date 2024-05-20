--- 
+++ 
@@ -3,7 +3,7 @@
     if height > 0:
         helper = ({1, 2, 3} - {start} - {end}).pop()
         steps.extend(hanoi(height - 1, start, helper))
-        steps.append((start, helper))
+        steps.append((start, end))
         steps.extend(hanoi(height - 1, helper, end))
 
     return steps
