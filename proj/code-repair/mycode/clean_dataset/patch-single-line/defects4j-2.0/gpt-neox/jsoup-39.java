--- 
+++ 
@@ -41,6 +41,7 @@
         docData = Charset.forName(defaultCharset).decode(byteData).toString();
         docData = docData.substring(1);
         charsetName = defaultCharset;
+        doc = null;
     }
     if (doc == null) {
         doc = parser.parseInput(docData, baseUri);
