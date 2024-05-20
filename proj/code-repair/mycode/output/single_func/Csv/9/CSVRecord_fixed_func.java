    <M extends Map<String, String>> M putIn(final M map) {
       if (values == null) {
            return map;
        }
        for (final Entry<String, Integer> entry : mapping.entrySet()) {
            final int col = entry.getValue().intValue();
            if (col < values.length) {
                map.put(entry.getKey(), values[col]);
            }
        }
        return map;
    }
