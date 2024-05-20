    public RectangularCholeskyDecomposition(RealMatrix matrix, double small)
        throws NonPositiveDefiniteMatrixException {
        final int order = matrix.getRowDimension();
        final double[][] c = matrix.getData();
        final double[][] b = new double[order][order];
           int[] swap  = new int[order];
            int[] index = new int[order];
            for (int i = 0; i < order; ++i) {
                index[i] = i;
            }
            int r = 0;
            for (boolean loop = true; loop;) {
                swap[r] = r;
                for (int i = r + 1; i < order; ++i) {
                    int ii  = index[i];
                    int isi = index[swap[i]];
                    if (c[ii][ii] > c[isi][isi]) {
                        swap[r] = i;
                    }
                }
                if (swap[r] != r) {
                    int tmp = index[r];
                    index[r] = index[swap[r]];
                    index[swap[r]] = tmp;
                }
                int ir = index[r];
                if (c[ir][ir] < small) {
                    if (r == 0) {
                        throw new NonPositiveDefiniteMatrixException(c[ir
                    for (int j = r + 1; j < i; ++j) {
                        final int ij = index[j];
                        final double f = c[ii][ij] - e * b[j][r];
                        c[ii][ij] = f;
                        c[ij][ii] = f;
                    }
                }
                loop = ++r < order;
            }
        }
        rank = r;
        root = MatrixUtils.createRealMatrix(order, r);
        for (int i = 0; i < order; ++i) {
            for (int j = 0; j < r; ++j) {
                root.setEntry(index[i], j, b[i][j]);
            }
        }
    }
