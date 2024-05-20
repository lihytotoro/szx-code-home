--- 
+++ 
@@ -11,7 +11,8 @@
             if (rhs.isNaN()) {
                 ret = this.isNaN();
             } else {
-                ret = (Double.doubleToRawLongBits(real) == Double.doubleToRawLongBits(rhs.getReal())) && (Double.doubleToRawLongBits(imaginary) == Double.doubleToRawLongBits(rhs.getImaginary())); 
+                ret = this.getReal() == rhs.getReal() &&
+                    this.getImaginary() == rhs.getImaginary();
             }
         } catch (ClassCastException ex) {
             // ignore exception
