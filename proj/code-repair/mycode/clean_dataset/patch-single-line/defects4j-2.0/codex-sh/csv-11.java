--- 
+++ 
@@ -23,7 +23,7 @@
             for (int i = 0; i < headerRecord.length; i++) {
                 final String header = headerRecord[i];
                 final boolean containsHeader = hdrMap.containsKey(header);
-                final boolean emptyHeader = header.trim().isEmpty();
+                final boolean emptyHeader = header == null || header.trim().isEmpty();
                 if (containsHeader && (!emptyHeader || (emptyHeader && !this.format.getIgnoreEmptyHeaders()))) {
                     throw new IllegalArgumentException("The header contains a duplicate name: \"" + header +
                             "\" in " + Arrays.toString(headerRecord));
