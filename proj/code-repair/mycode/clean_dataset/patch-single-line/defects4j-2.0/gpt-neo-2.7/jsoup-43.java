--- 
+++ 
@@ -4,7 +4,7 @@
 
     for (int i = 0; i < elements.size(); i++) {
         E element = elements.get(i);
-        if (element.equals(search))
+        if (element == search)
             return i;
     }
     return null;
