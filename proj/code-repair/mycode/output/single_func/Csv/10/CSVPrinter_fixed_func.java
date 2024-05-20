    public CSVPrinter(final Appendable out, final CSVFormat format) throws IOException {
        Assertions.notNull(out, "out");
        Assertions.notNull(format, "format");
        this.out = out;
        this.format = format;
        this.format.validate();
       this.delimiter = format.getDelimiter();
        this.escape = format.getEscape();
        this.quote = format.getQuote();
    }
