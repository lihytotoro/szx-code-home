--- 
+++ 
@@ -41,7 +41,7 @@
                     break;
                 case '<':
                     // escape when in character data or when in a xml attribue val; not needed in html attr val
-                    if (!inAttribute)
+                    if (!inAttribute || escapeMode == EscapeMode.xhtml)
                         accum.append("&lt;");
                     else
                         accum.append(c);
