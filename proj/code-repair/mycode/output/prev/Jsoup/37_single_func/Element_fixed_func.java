    public String html() {
        StringBuilder accum = new StringBuilder();
        html(accum);
        return StringEscapeUtils.escapeHtml(accum.toString()).trim();
    }
