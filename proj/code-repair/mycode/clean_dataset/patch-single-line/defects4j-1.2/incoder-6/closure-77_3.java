--- 
+++ 
@@ -8,6 +8,9 @@
   for (int i = 0; i < s.length(); i++) {
     char c = s.charAt(i);
     switch (c) {
+      case 0:
+        sb.append("\\0");
+        break;
       case '\n': sb.append("\\n"); break;
       case '\r': sb.append("\\r"); break;
       case '\t': sb.append("\\t"); break;
