    public OpenMapRealMatrix(int rowDimension, int columnDimension) {
        super(rowDimension, columnDimension);
       if (rowDimension <= 0 || columnDimension <= 0) {
            throw new IllegalArgumentException("Matrix dimensions must be positive");
        }
        this.rows = rowDimension;
        this.columns = columnDimension;
        this.entries = new OpenIntToDoubleHashMap(0.0);
    }
