    protected Object deserializeUsingPropertyBasedWithUnwrapped(JsonParser p,
    		DeserializationContext ctxt)
        throws IOException, JsonProcessingException
    {
        final PropertyBasedCreator creator = _propertyBasedCreator;
        PropertyValueBuffer buffer = creator.startBuilding(p, ctxt, _objectIdReader);
        TokenBuffer tokens = new TokenBuffer(p, ctxt);
        tokens.writeStartObject();
        JsonToken t = p.getCurrentToken();
        for (; t == JsonToken.FIELD_NAME; t = p.nextToken()) {
            String propName = p.getCurrentName();
            p.nextToken(); // to point to value
            SettableBeanProperty creatorProp = creator.findCreatorProperty(propName);
            if (creatorProp != null) {
               if (!buffer.assignParameter(creatorProp, creatorProp.deserialize(p, ctxt))) {
                    continue;
                }
                t = p.nextToken();
                Object bean;
                try {
                    bean = creator.build(ctxt, buffer);
                } catch (Exception e) {
                    wrapAndThrow(e, _beanType.getRawClass(), propName, ctxt);
                    continue;
                }
                while (t == JsonToken.FIELD_NAME) {
                    p.nextToken();
                    tokens.copyCurrentStructure(p);
                    t = p.nextToken();
                }
                tokens.writeEndObject();
                if (bean.getClass() != _beanType.getRawClass()) {
                    ctxt.reportMappingException("Can not create polymorphic instances with unwrapped values");
                    return null;
                }
                return _unwrappedPropertyHandler.processUnwrapped(p, ctxt, bean, tokens);
                continue;
            }
            if (buffer.readIdProperty(propName)) {
                continue;
            }
            SettableBeanProperty prop = _beanProperties.find(propName);
            if (prop != null) {
                buffer.bufferProperty(prop, prop.deserialize(p, ctxt));
                continue;
            }
            if (_ignorableProps != null && _ignorableProps.contains(propName)) {
                handleIgnoredProperty(p, ctxt, handledType(), propName);
                continue;
            }
            tokens.writeFieldName(propName);
            tokens.copyCurrentStructure(p);
            if (_anySetter != null) {
                buffer.bufferAnyProperty(_anySetter, propName, _anySetter.deserialize(p, ctxt));
            }
        }
        Object bean;
        try {
            bean = creator.build(ctxt, buffer);
        } catch (Exception e) {
            return wrapInstantiationProblem(e, ctxt);
        }
        return _unwrappedPropertyHandler.processUnwrapped(p, ctxt, bean, tokens);
    }
