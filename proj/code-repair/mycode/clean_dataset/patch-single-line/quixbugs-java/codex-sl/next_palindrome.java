--- 
+++ 
@@ -19,7 +19,7 @@
 
     ArrayList<Integer> otherwise = new ArrayList<Integer>();
 otherwise.add(1);
-otherwise.addAll(Collections.nCopies(digit_list.length, 0));
+    otherwise.addAll(Collections.nCopies(digit_list.length - 1, 0));
 otherwise.add(1);
 
     return String.valueOf(otherwise);
