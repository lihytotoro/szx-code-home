--- 
+++ 
@@ -36,7 +36,7 @@
             {
                 // if the value is not yes, true or 1 then don't add the
                 // option to the CommandLine
-                break;
+                continue;
             }
 
             cmd.addOption(opt);
