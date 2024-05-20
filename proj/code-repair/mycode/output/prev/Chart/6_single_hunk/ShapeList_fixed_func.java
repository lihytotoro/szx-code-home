    public boolean equals(Object obj) {
    
        if (obj == this) {
            return true;
        }
        if (!(obj instanceof ShapeList)) {
            return false;
        }
    return obj.equals(this);
    
    }
