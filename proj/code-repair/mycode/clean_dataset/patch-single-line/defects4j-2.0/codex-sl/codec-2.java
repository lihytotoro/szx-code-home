--- 
+++ 
@@ -30,7 +30,7 @@
                 }
                 break;
         }
-        if (lineLength > 0) {
+        if (lineLength > 0 && pos > 0) { // Finish off the current line.
             System.arraycopy(lineSeparator, 0, buf, pos, lineSeparator.length);
             pos += lineSeparator.length;
         }
