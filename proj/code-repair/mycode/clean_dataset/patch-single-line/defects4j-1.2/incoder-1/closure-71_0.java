--- 
+++ 
@@ -7,7 +7,8 @@
   if (objectType != null) {
     // Is this a normal property access, or are we trying to override
     // an existing property?
-    boolean isOverride = t.inGlobalScope() &&
+    boolean isOverride =
+        parent.getJSDocInfo() != null &&
         parent.getType() == Token.ASSIGN &&
         parent.getFirstChild() == getprop;
 
