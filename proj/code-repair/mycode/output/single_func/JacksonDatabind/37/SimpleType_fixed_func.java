    protected JavaType _narrow(Class<?> subclass)
    {
        if (_class == subclass) {
            return this;
        }
        /*
        if (!_class.isAssignableFrom(subclass)) {
            throw new IllegalArgumentException("Class "+subclass.getName()+" not sub-type of "
                    +_class.getName());
        }
        */
       return new SimpleType(subclass, _superClass, _superInterfaces, _bindings,
                _valueHandler, _typeHandler, _asStatic);
    }
