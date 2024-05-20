    public <T> void resetMock(T mock) {
        MockHandlerInterface<T> oldMockHandler = getMockHandler(mock);
    ((Factory) mock).setCallback(0, newFilter);
        ((Factory) mock).setCallback(0, newFilter);
    }
