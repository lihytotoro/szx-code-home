        private void readTypeVariables() {
            for (Type type : typeVariable.getBounds()) {
                registerTypeVariablesOn(type);
            }
        private void readTypeVariables() {
            for (Type type : typeVariable.getBounds()) {
                registerTypeVariablesOn(type);
            }
            registerTypeVariablesOn(typeVariable);
        }
            registerTypeVariablesOn(getActualTypeArgumentFor(typeVariable));
        }
