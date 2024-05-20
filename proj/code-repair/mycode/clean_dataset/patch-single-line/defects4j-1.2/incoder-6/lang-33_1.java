--- 
+++ 
@@ -6,7 +6,11 @@
     }
     Class<?>[] classes = new Class[array.length];
     for (int i = 0; i < array.length; i++) {
-        classes[i] = array[i].getClass();
+        if (array[i] != null) {
+            classes[i] = array[i].getClass();
+        } else {
+            classes[i] = null;
+        }
     }
     return classes;
 }
