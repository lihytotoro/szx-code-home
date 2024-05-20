--- 
+++ 
@@ -3,5 +3,5 @@
         _annotations = new HashMap<Class<? extends Annotation>,Annotation>();
     }
     Annotation previous = _annotations.put(ann.annotationType(), ann);
-    return (previous != null) && previous.equals(ann);
+    return previous == null ? true : previous.equals(ann);
 }
