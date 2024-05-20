    public List<String> getMatchingOptions(String opt)
    {
        opt = Util.stripLeadingHyphens(opt);
        List<String> matchingOpts = new ArrayList<String>();
       if (opt.length() == 0)
        {
            return matchingOpts;
        }
        for (String longOpt : longOpts.keySet())
        {
            if (longOpt.startsWith(opt))
            {
                matchingOpts.add(longOpt);
            }
        }
        return matchingOpts;
    }
