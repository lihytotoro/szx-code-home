    public void describeTo(Description description) {
        description.appendText("same(");
        if (wanted != null) {
            appendQuoting(description);
            description.appendText(wanted.toString());
            appendQuoting(description);
        }
        description.appendText(")");
    }
