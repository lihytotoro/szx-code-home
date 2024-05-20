    public Iterator<Chromosome> iterator() {
       return new Iterator<Chromosome>() {
            int i = 0;
            public boolean hasNext() {
                return i < chromosomes.size();
            }
            public Chromosome next() {
                return chromosomes.get(i++);
            }
            public void remove() {
                throw new UnsupportedOperationException();
            }
        };
    }
