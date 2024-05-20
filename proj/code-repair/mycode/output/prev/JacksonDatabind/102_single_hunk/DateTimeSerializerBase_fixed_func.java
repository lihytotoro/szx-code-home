    public JsonSerializer<?> createContextual(SerializerProvider serializers,
            BeanProperty property) throws JsonMappingException
    {
        // Note! Should not skip if `property` null since that'd skip check
        // for config overrides, in case of root value
    if (property == null) {
        return this;
    }
        JsonFormat.Value format = findFormatOverrides(serializers, property, handledType());
        if (format == null) {
            return this;
        }
        // Simple case first: serialize as numeric timestamp?
        JsonFormat.Shape shape = format.getShape();
        if (shape.isNumeric()) {
            return withFormat(Boolean.TRUE, null);
        }
    
        // 08-Jun-2017, tatu: With [databind#1648], this gets bit tricky..
        // First: custom pattern will override things
        if (format.hasPattern()) {
            final Locale loc = format.hasLocale()
                            ? format.getLocale()
                            : serializers.getLocale();
            SimpleDateFormat df = new SimpleDateFormat(format.getPattern(), loc);
            TimeZone tz = format.hasTimeZone() ? format.getTimeZone()
                    : serializers.getTimeZone();
            df.setTimeZone(tz);
            return withFormat(Boolean.FALSE, df);
        }
    
        // Otherwise, need one of these changes:
        final boolean hasLocale = format.hasLocale();
        final boolean hasTZ = format.hasTimeZone();
        final boolean asString = (shape == JsonFormat.Shape.STRING);
    
        if (!hasLocale && !hasTZ && !asString) {
            return this;
        }
    
        DateFormat df0 = serializers.getConfig().getDateFormat();
        // Jackson's own `StdDateFormat` is quite easy to deal with...
        if (df0 instanceof StdDateFormat) {
            StdDateFormat std = (StdDateFormat) df0;
            if (format.hasLocale()) {
                std = std.withLocale(format.getLocale());
            }
            if (format.hasTimeZone()) {
                std = std.withTimeZone(format.getTimeZone());
            }
            return withFormat(Boolean.FALSE, std);
        }
    
        // 08-Jun-2017, tatu: Unfortunately there's no generally usable
        //    mechanism for changing `DateFormat` instances (or even clone()ing)
        //    So: require it be `SimpleDateFormat`; can't config other types
        if (!(df0 instanceof SimpleDateFormat)) {
            serializers.reportBadDefinition(handledType(), String.format(
    figured `DateFormat` (%s) not a `SimpleDateFormat`; cannot configure `Locale` or `TimeZone`",
    getClass().getName()));
        }
        SimpleDateFormat df = (SimpleDateFormat) df0;
        if (hasLocale) {
            // Ugh. No way to change `Locale`, create copy; must re-crete completely:
            df = new SimpleDateFormat(df.toPattern(), format.getLocale());
        } else {
            df = (SimpleDateFormat) df.clone();
        }
        TimeZone newTz = format.getTimeZone();
        boolean changeTZ = (newTz != null) && !newTz.equals(df.getTimeZone());
        if (changeTZ) {
            df.setTimeZone(newTz);
        }
        return withFormat(Boolean.FALSE, df);
    }
