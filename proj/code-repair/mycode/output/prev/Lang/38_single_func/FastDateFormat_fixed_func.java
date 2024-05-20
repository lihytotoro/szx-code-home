    public StringBuffer format(Calendar calendar, StringBuffer buf) {
        if (mTimeZoneForced) {
            Calendar newCalendar = (Calendar) calendar.clone();
            newCalendar.setTimeZone(mTimeZone);
            return applyRules(newCalendar, buf);
        } else {
            return applyRules(calendar, buf);
        }
    }
