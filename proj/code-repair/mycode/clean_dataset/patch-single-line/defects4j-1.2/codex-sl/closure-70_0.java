--- 
+++ 
@@ -9,7 +9,7 @@
       for (Node astParameter : astParameters.children()) {
         if (jsDocParameter != null) {
           defineSlot(astParameter, functionNode,
-              jsDocParameter.getJSType(), true);
+              jsDocParameter.getJSType(), false);
           jsDocParameter = jsDocParameter.getNext();
         } else {
           defineSlot(astParameter, functionNode, null, true);
