        protected JSType caseTopType(JSType topType) {
          return topType.getLeastSupertype(ARRAY_TYPE);
        }
