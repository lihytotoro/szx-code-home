--- 
+++ 
@@ -3,8 +3,7 @@
     if (vals.length != dim) {
         throw new DimensionMismatchException(vals.length, dim);
     }
-
-    return FastMath.pow(2 * FastMath.PI, -dim / 2) *
+    return FastMath.pow(2 * FastMath.PI, -dim / 2.0) *
         FastMath.pow(covarianceMatrixDeterminant, -0.5) *
         getExponentTerm(vals);
 }
