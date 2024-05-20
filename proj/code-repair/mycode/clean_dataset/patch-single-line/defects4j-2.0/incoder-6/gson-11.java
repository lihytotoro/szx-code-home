--- 
+++ 
@@ -6,6 +6,8 @@
     return null;
   case NUMBER:
     return new LazilyParsedNumber(in.nextString());
+  case STRING:
+    return new LazilyParsedNumber(in.nextString());
   default:
     throw new JsonSyntaxException("Expecting number, got: " + jsonToken);
   }
