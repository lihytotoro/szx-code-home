--- 
+++ 
@@ -1,4 +1,4 @@
 public double[] fit() {
     final double[] guess = (new ParameterGuesser(getObservations())).guess();
-    return fit(new Gaussian.Parametric(), guess);
+    return fit(guess);
 }
