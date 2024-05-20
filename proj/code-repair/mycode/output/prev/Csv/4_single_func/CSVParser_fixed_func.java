    public Map<String, Integer> getHeaderMap() {
        if (this.headerMap == null) {
            this.headerMap = new LinkedHashMap<String, Integer>();
        }
        return new LinkedHashMap<String, Integer>(this.headerMap);
    }
