    public void setSelected(Option option) throws AlreadySelectedException
    {
        if (option == null)
        {
            selected = null;
            return;
        }
       if (selected == null || selected.getOpt().equals(option.getOpt()))
        {
            selected = option;
        }
        else
        {
            throw new AlreadySelectedException(this, option);
        }
    }
