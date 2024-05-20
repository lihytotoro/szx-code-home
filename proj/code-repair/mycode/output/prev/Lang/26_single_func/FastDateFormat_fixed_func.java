    public String format(Date date) {
        Calendar c = new GregorianCalendar(mTimeZone);
        c.setTime(date);
        WeekOfYear week = new WeekOfYear(c);
        return applyRules(c, new StringBuffer(mMaxLengthEstimate)).toString();
    }
