--- 
+++ 
@@ -9,7 +9,7 @@
             } else {
                 double r = correlationMatrix.getEntry(i, j);
                 double t = Math.abs(r * Math.sqrt((nObs - 2)/(1 - r * r)));
-                out[i][j] = 2 * (1 - tDistribution.cumulativeProbability(t));
+                out[i][j] = 2 * tDistribution.cumulativeProbability(-t);
             }
         }
     }
