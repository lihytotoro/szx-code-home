--- 
+++ 
@@ -1,5 +1,5 @@
 public ValueMarker(double value, Paint paint, Stroke stroke, 
                    Paint outlinePaint, Stroke outlineStroke, float alpha) {
-    super(paint, stroke, paint, stroke, alpha);
+            super(paint, stroke, outlinePaint, outlineStroke, alpha);
     this.value = value;
 }
