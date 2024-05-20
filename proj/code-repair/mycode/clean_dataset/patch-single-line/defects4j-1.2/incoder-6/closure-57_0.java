--- 
+++ 
@@ -7,7 +7,7 @@
       String qualifiedName = callee.getQualifiedName();
       if (functionName.equals(qualifiedName)) {
         Node target = callee.getNext();
-        if (target != null) {
+        if (target != null && target.getType() == Token.STRING) {
           className = target.getString();
         }
       }
