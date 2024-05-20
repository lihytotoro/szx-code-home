    protected SettableBeanProperty constructSetterlessProperty(DeserializationContext ctxt,
            BeanDescription beanDesc, BeanPropertyDefinition propDef)
        throws JsonMappingException
    {
        JavaType propertyType = propDef.getGetter().getParameterType(0);
        SetterlessProperty prop = new SetterlessProperty(propDef.getName(), propertyType, propDef.getGetter());
        return prop;
    }
