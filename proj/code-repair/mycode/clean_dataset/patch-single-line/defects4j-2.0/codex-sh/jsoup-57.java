--- 
+++ 
@@ -4,7 +4,8 @@
         return;
     for (Iterator<String> it = attributes.keySet().iterator(); it.hasNext(); ) {
         String attrKey = it.next();
-        if (attrKey.equalsIgnoreCase(key))
-            attributes.remove(attrKey);
+        if (attrKey.equalsIgnoreCase(key)) {
+            it.remove();
+        }
     }
 }
