--- 
+++ 
@@ -8,6 +8,7 @@
         } else { // can NOT suppress entries in tabular output
             jgen.writeNull();
         }
+        return;
     }
     // otherwise find serializer to use
     JsonSerializer<Object> ser = _serializer;
