--- 
+++ 
@@ -4,6 +4,7 @@
     while (node != null) {
         nextnode = node.getSuccessor();
         node.setSuccessor(prevnode);
+prevnode = node;
         node = nextnode;
     }
     return prevnode;
