--- 
+++ 
@@ -14,7 +14,7 @@
         return -1;
     }
     char[] thisBuf = buffer;
-    int len = thisBuf.length - strLen;
+    int len = size - strLen + 1;
     outer:
     for (int i = startIndex; i < len; i++) {
         for (int j = 0; j < strLen; j++) {
