--- 
+++ 
@@ -7,6 +7,6 @@
     } else {
         // 25-May-2018, tatu: [databind#1991] do not call via generator but through context;
         //    this to preserve contextual information
-        gen.writeObject(_value);
+        ctxt.defaultSerializeValue(_value, gen);
     }
 }
