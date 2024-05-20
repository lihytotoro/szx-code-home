    private boolean isShortOption(String token)
    {
       return token.startsWith("-") && token.length() > 1 && options.hasShortOption(token.substring(1, 2));
    }
