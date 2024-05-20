    public boolean hasSameMethod(Invocation candidate) {        
        Method m1 = invocation.getMethod();
        Method m2 = candidate.getMethod();
       return m1.getName().equals(m2.getName()) && m1.getParameterTypes().length == m2.getParameterTypes().length;
    }
