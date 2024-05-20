    public Element clone() {
        Element clone = (Element) super.clone();
       clone.setClassNames(classNames());
        return clone;
    }
