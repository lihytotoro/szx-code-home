    public <T> void resetMock(T mock) {
        MockHandlerInterface<T> oldMockHandler = getMockHandler(mock);
       MethodInterceptorFilter newFilter = new MethodInterceptorFilter(oldMockHandler, (MockSettingsImpl) org.mockito.Mockito.withSettings().defaultAnswer(org.mockito.Mockito.RETURNS_DEFAULTS));
        ((Factory) mock).setCallback(0, newFilter);
    }
