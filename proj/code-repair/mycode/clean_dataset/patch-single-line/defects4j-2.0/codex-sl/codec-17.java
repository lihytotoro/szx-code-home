--- 
+++ 
@@ -1,3 +1,3 @@
 public static String newStringIso8859_1(final byte[] bytes) {
-    return new String(bytes, Charsets.ISO_8859_1);
+		return StringUtils.newString(bytes, CharEncoding.ISO_8859_1);
 }
