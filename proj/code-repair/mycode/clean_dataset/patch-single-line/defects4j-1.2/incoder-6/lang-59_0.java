--- 
+++ 
@@ -4,7 +4,7 @@
         String str = (obj == null ? getNullText() : obj.toString());
         int strLen = str.length();
         if (strLen >= width) {
-            str.getChars(0, strLen, buffer, size);
+            str.getChars(0, width, buffer, size);
         } else {
             int padLen = width - strLen;
             str.getChars(0, strLen, buffer, size);
