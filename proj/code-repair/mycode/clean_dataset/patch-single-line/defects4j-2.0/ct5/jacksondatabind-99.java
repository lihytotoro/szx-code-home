--- 
+++ 
@@ -4,5 +4,6 @@
     sb.append(_class.getName());
     sb.append('<');
     sb.append(_referencedType.toCanonical());
+sb.append('>');
     return sb.toString();
 }
