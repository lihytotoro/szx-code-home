--- 
+++ 
@@ -1,3 +1,3 @@
 public Iterator<Chromosome> iterator() {
-    return chromosomes.iterator();
+        return Collections.unmodifiableList(getChromosomes()).iterator();
 }
