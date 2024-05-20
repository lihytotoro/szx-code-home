        private void readTypeVariables() {
            for (Type type : typeVariable.getBounds()) {
                registerTypeVariablesOn(type);
            }
           if (getActualTypeArgumentFor(typeVariable) != null)
            registerTypeVariablesOn(getActualTypeArgumentFor(typeVariable));
        }
