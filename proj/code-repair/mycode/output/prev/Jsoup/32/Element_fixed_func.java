    public Element clone() {
        Element clone = (Element) super.clone();
        clone.classNames = new HashSet<>(classNames);
        return clone;
    }
