--- 
+++ 
@@ -36,7 +36,7 @@
         System.arraycopy(iValues, i, newValues, i + 1, newValues.length - i - 1);
         // use public constructor to ensure full validation
         // this isn't overly efficient, but is safe
-        Partial newPartial = new Partial(iChronology, newTypes, newValues);
+        Partial newPartial = new Partial(newTypes, newValues);
         iChronology.validate(newPartial, newValues);
         return newPartial;
     }
