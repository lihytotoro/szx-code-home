--- 
+++ 
@@ -1,3 +1,3 @@
 public static boolean isAvailableLocale(Locale locale) {
-    return cAvailableLocaleSet.contains(locale);
+		return Arrays.asList(Locale.getAvailableLocales()).contains(locale);
 }
