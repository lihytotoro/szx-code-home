    protected boolean equal(
        EvalContext context,
        Expression left,
        Expression right) 
    {
        Object l = left.compute(context);
        Object r = right.compute(context);
       if (l instanceof EvalContext) {
            l = ((EvalContext) l).getSingleNodePointer();
        }
        if (r instanceof EvalContext) {
            r = ((EvalContext) r).getSingleNodePointer();
        }
        if (l instanceof Collection) {
            l = ((Collection) l).iterator();
        }
        if (r instanceof Collection) {
            r = ((Collection) r).iterator();
        }
        if ((l instanceof Iterator) && !(r instanceof Iterator)) {
            return contains((Iterator) l, r);
        }
        if (!(l instanceof Iterator) && (r instanceof Iterator)) {
            return contains((Iterator) r, l);
        }
        if (l instanceof Iterator && r instanceof Iterator) {
            return findMatch((Iterator) l, (Iterator) r);
        }
        return equal(l, r);
    }
