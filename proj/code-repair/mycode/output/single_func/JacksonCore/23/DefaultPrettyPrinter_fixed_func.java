    public DefaultPrettyPrinter createInstance() {
       DefaultPrettyPrinter defaultPrettyPrinter = new DefaultPrettyPrinter();
        defaultPrettyPrinter.configure(this);
        return defaultPrettyPrinter;
    }
        return new DefaultPrettyPrinter(this);
    }
