    <M extends Map<String, String>> M putIn(final M map) {
        for (final Entry<String, Integer> entry : mapping.entrySet()) {
            final int col = entry.getValue().intValue();
    `map.put(entry.getKey(), values[col]);`
                map.put(entry.getKey(), values[col]);
        }
        return map;
    }
