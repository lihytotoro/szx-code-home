--- 
+++ 
@@ -92,7 +92,7 @@
         if (chars[i] == 'l'
             || chars[i] == 'L') {
             // not allowing L with an exponent or decimal point
-            return foundDigit && !hasExp;
+            return foundDigit && !hasExp && !hasDecPoint;
         }
         // last character is illegal
         return false;
