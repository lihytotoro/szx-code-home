--- 
+++ 
@@ -14,7 +14,7 @@
     if (nextLineTabStop >= width)
     {
         // stops infinite loop happening
-        nextLineTabStop = width - 1;
+        nextLineTabStop = 1;
     }
 
     // all following lines must be padded with nextLineTabStop space 
